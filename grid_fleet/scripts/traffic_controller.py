#!/usr/bin/env python3

import threading
import rospy
from std_msgs.msg import String
from grid_fleet.srv import RequestMove, RequestMoveResponse

# ── Thresholds ────────────────────────────────────────────────────────────────

# Seconds a vehicle must wait before it earns a priority reservation
PRIORITY_WAIT_THRESHOLD = 5.0

# Seconds before a stuck vehicle triggers a force-clear 
FORCE_CLEAR_THRESHOLD = 8.0

# ── Shared state ──────────────────────────────────────────────────────────────

# (x,y) -> vehicle_id — which vehicle owns each cell right now
occupied_cells = {}

# vehicle_id -> (x,y) — last known position of each vehicle
vehicle_positions = {}

# vehicle_id -> (x,y) — where each vehicle is currently trying to go
pending_moves = {}

# vehicle_id -> float — ROS timestamp when the vehicle started waiting
waiting_since = {}

# (x,y) -> vehicle_id — priority-reserved cells; other vehicles must avoid these
# A vehicle earns a reservation on its target after waiting > PRIORITY_WAIT_THRESHOLD
priority_reservations = {}

# frozenset({vA, vB}) -> int — how many times each pair has deadlocked
deadlock_counts = {}

# frozenset({vA, vB}) -> vehicle_id — who lost the last deadlock in each pair
deadlock_loser = {}

# Prevents race conditions when multiple vehicles call /request_move at once
lock = threading.Lock()


# ── Movement validation ───────────────────────────────────────────────────────

def is_valid_move(current_x, current_y, target_x, target_y):
    """Return (True, '') or (False, reason). Cardinal moves only, exactly 1 cell."""
    dx = abs(target_x - current_x)
    dy = abs(target_y - current_y)

    if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
        return True, ""
    if dx == 0 and dy == 0:
        return False, "No movement — already at target"
    if dx > 1 or dy > 1:
        return False, f"Multi-cell jump not allowed: distance ({dx},{dy})"
    return False, f"Diagonal move not allowed: ({current_x},{current_y}) -> ({target_x},{target_y})"


# ── Swap-deadlock detection ───────────────────────────────────────────────────

def is_deadlock(vehicle_id, target_x, target_y):
    """True if vehicle_id and the occupant of (target_x,target_y) want each other's cell."""
    my_pos = vehicle_positions.get(vehicle_id)
    if my_pos is None:
        return False

    blocker = occupied_cells.get((target_x, target_y))
    if blocker is None:
        return False

    blocker_target = pending_moves.get(blocker)
    if blocker_target is None:
        return False

    if blocker_target == my_pos:
        rospy.logwarn(
            f"[TrafficController] DEADLOCK detected! "
            f"{vehicle_id} at {my_pos} wants {(target_x, target_y)} "
            f"AND {blocker} wants {my_pos}"
        )
        return True

    return False


# ── Deadlock priority (alternates each occurrence) ────────────────────────────

def get_priority_vehicle(vehicle_a, vehicle_b):
    """Pick which vehicle wins a deadlock. Alternates winner to prevent starvation."""
    pair = frozenset({vehicle_a, vehicle_b})

    last_loser = deadlock_loser.get(pair)
    if last_loser is not None:
        winner = last_loser
        loser  = vehicle_b if winner == vehicle_a else vehicle_a
    else:
        wait_a = waiting_since.get(vehicle_a, rospy.get_time())
        wait_b = waiting_since.get(vehicle_b, rospy.get_time())
        if wait_a < wait_b:
            winner, loser = vehicle_a, vehicle_b
        elif wait_b < wait_a:
            winner, loser = vehicle_b, vehicle_a
        else:
            winner = min(vehicle_a, vehicle_b)
            loser  = vehicle_b if winner == vehicle_a else vehicle_a

    deadlock_loser[pair] = loser
    deadlock_counts[pair] = deadlock_counts.get(pair, 0) + 1

    if deadlock_counts[pair] >= 3:
        rospy.logwarn(
            f"[TrafficController] Pair {vehicle_a}/{vehicle_b} "
            f"has deadlocked {deadlock_counts[pair]} times — possible path loop!"
        )

    return winner


# ── FIX: priority reservation management ─────────────────────────────────────

def update_priority_reservations():
    """
    Any vehicle waiting longer than PRIORITY_WAIT_THRESHOLD earns a priority
    reservation on its target cell. This blocks other vehicles from entering
    that cell — they must reroute — until the waiting vehicle arrives.
    """
    now = rospy.get_time()
    for vehicle_id, start_time in waiting_since.items():
        waited = now - start_time
        target = pending_moves.get(vehicle_id)
        if target is None:
            continue
        if waited >= PRIORITY_WAIT_THRESHOLD:
            if priority_reservations.get(target) != vehicle_id:
                priority_reservations[target] = vehicle_id
                rospy.logwarn(
                    f"[TrafficController] PRIORITY RESERVATION: {vehicle_id} waited "
                    f"{waited:.1f}s — cell {target} is now reserved. "
                    f"Other vehicles must reroute."
                )


# ── ROS callback: position update ─────────────────────────────────────────────

def parse_position(msg):
    """Update state when a vehicle publishes its new position."""
    try:
        parts = msg.data.split()
        if len(parts) != 3:
            return

        vehicle_id = parts[0]
        new_x = int(parts[1])
        new_y = int(parts[2])

        with lock:
            old_pos = vehicle_positions.get(vehicle_id)

            # Free the old cell if we own it
            if old_pos is not None:
                if occupied_cells.get(old_pos) == vehicle_id:
                    del occupied_cells[old_pos]

            # Claim the new cell
            vehicle_positions[vehicle_id] = (new_x, new_y)
            occupied_cells[(new_x, new_y)] = vehicle_id

            # FIX: release priority reservation now that the vehicle arrived
            if priority_reservations.get((new_x, new_y)) == vehicle_id:
                del priority_reservations[(new_x, new_y)]
                rospy.loginfo(
                    f"[TrafficController] {vehicle_id} reached reserved cell "
                    f"{(new_x, new_y)} — reservation released"
                )

            # Clear pending move and wait timer if this was the intended target
            if pending_moves.get(vehicle_id) == (new_x, new_y):
                del pending_moves[vehicle_id]
                waiting_since.pop(vehicle_id, None)

    except Exception as e:
        rospy.logwarn(f"[TrafficController] Failed to parse position: {e}")


# ── ROS service: move approval ────────────────────────────────────────────────

def handle_move_request(req):
    """Main approval logic. Called by vehicles via the /request_move service."""
    with lock:

        vehicle_id = req.vehicle_id
        target_x   = req.target_x
        target_y   = req.target_y
        current_x  = req.current_x
        current_y  = req.current_y
        target     = (target_x, target_y)

        response = RequestMoveResponse()

        # Update priority reservations before processing this request
        update_priority_reservations()

        # 1. Out-of-bounds check
        if not (0 <= target_x <= 7 and 0 <= target_y <= 7):
            response.approved = False
            response.reason = f"Out of bounds: {target}"
            rospy.logwarn(f"[TrafficController] {vehicle_id} rejected — out of bounds")
            return response

        # 2. Movement rule check (orthogonal, exactly 1 cell)
        valid, reason = is_valid_move(current_x, current_y, target_x, target_y)
        if not valid:
            response.approved = False
            response.reason = reason
            rospy.logwarn(f"[TrafficController] {vehicle_id} rejected — {reason}")
            return response

        # 3. Already at target — nothing to do
        if target_x == current_x and target_y == current_y:
            response.approved = True
            response.reason = "Already at target"
            return response

        # Record intent and start wait timer
        pending_moves[vehicle_id] = target
        if vehicle_id not in waiting_since:
            waiting_since[vehicle_id] = rospy.get_time()

        occupant = occupied_cells.get(target)

        # ── Case A: cell is free ──────────────────────────────────────────────
        if occupant is None:

            # Block entry if another vehicle has a priority reservation here
            reserver = priority_reservations.get(target)
            if reserver is not None and reserver != vehicle_id:
                rospy.loginfo(
                    f"[TrafficController] X {vehicle_id} blocked from {target} "
                    f"— priority reservation held by {reserver}"
                )
                response.approved = False
                response.reason = f"Cell reserved by {reserver} (priority)"
                return response

            # Cell is free and not reserved — approve the move
            if occupied_cells.get((current_x, current_y)) == vehicle_id:
                del occupied_cells[(current_x, current_y)]

            occupied_cells[target] = vehicle_id
            vehicle_positions[vehicle_id] = target
            pending_moves.pop(vehicle_id, None)
            waiting_since.pop(vehicle_id, None)

            response.approved = True
            response.reason = "Cell is free"
            rospy.loginfo(
                f"[TrafficController] v {vehicle_id} approved: "
                f"({current_x},{current_y}) -> {target}"
            )
            return response

        # ── Case B: vehicle already owns the cell (position lag) ──────────────
        elif occupant == vehicle_id:
            response.approved = True
            response.reason = "Already owns cell"
            return response

        # ── Case C: cell occupied by someone else ─────────────────────────────
        else:
            deadlock = is_deadlock(vehicle_id, target_x, target_y)

            if deadlock:
                priority = get_priority_vehicle(vehicle_id, occupant)

                if priority == vehicle_id:
                    # We win — take the cell
                    rospy.loginfo(
                        f"[TrafficController] Deadlock broken — "
                        f"{vehicle_id} gets priority over {occupant}"
                    )

                    if occupied_cells.get((current_x, current_y)) == vehicle_id:
                        del occupied_cells[(current_x, current_y)]

                    occupied_cells[target] = vehicle_id
                    vehicle_positions[vehicle_id] = target
                    pending_moves.pop(vehicle_id, None)
                    waiting_since.pop(vehicle_id, None)

                    # Clear loser's intent so they re-plan next cycle
                    pending_moves.pop(occupant, None)
                    waiting_since.pop(occupant, None)

                    # Release any priority reservation the loser held
                    for cell, reserver in list(priority_reservations.items()):
                        if reserver == occupant:
                            del priority_reservations[cell]

                    rospy.loginfo(
                        f"[TrafficController] {occupant} pending move cleared "
                        f"— will re-plan on next request"
                    )

                    response.approved = True
                    response.reason = "Deadlock broken — priority granted"
                    return response

                else:
                    # We lose — must wait
                    rospy.loginfo(
                        f"[TrafficController] Deadlock — "
                        f"{vehicle_id} must wait for {occupant}"
                    )
                    response.approved = False
                    response.reason = f"Deadlock — waiting for {occupant} to move first"
                    return response

            else:
                # Normal rejection — cell is just occupied
                rospy.loginfo(
                    f"[TrafficController] X {vehicle_id} rejected — "
                    f"{target} occupied by {occupant}"
                )
                response.approved = False
                response.reason = f"Cell occupied by {occupant}"
                return response


# ── Grid display ──────────────────────────────────────────────────────────────

def print_grid():
    """Print an 8x8 ASCII map of current vehicle positions and reservations."""
    rospy.loginfo("--- GRID MAP (8x8) ---")
    # Maps each label to its position. 
    pos_map     = {"V" + vid[-1]: pos for vid, pos in vehicle_positions.items()} #Creates a display-friendly label for each vehicle. For example, "vehicle1" becomes "V1". 
    # Instead of label → position, it's position → label. This allows us to easily look up which vehicle (if any) is at each cell when printing the grid.
    pos_map_inv = {pos: label for label, pos in pos_map.items()}
    reserve_map = {pos: vid[-1] for pos, vid in priority_reservations.items()}

    for y in range(7, -1, -1):
        row = ""
        for x in range(8):
            if (x, y) in pos_map_inv:
                row += f"[{pos_map_inv[(x,y)]}]"
            elif (x, y) in reserve_map:
                row += f"[R{reserve_map[(x,y)]}]"   # reserved cell marker ex: R1 for reserved by vehicle1
            else:
                row += "[ . ]"
        rospy.loginfo(row)

    rospy.loginfo("----------------------")


# ── Long-wait monitor ─────────────────────────────────────────────────────────

def check_long_waiters():
    """Warn on long waits; force-clear the blocker after FORCE_CLEAR_THRESHOLD."""
    now = rospy.get_time()

    for vehicle_id, start_time in list(waiting_since.items()):
        waited = now - start_time
        target = pending_moves.get(vehicle_id, "unknown")

        # Warn at half the force-clear threshold
        if waited > FORCE_CLEAR_THRESHOLD / 2:
            rospy.logwarn(
                f"[TrafficController] {vehicle_id} has been waiting "
                f"{waited:.1f}s trying to reach {target}"
            )

        # Force-clear the blocker after threshold
        if waited > FORCE_CLEAR_THRESHOLD:
            target_pos = pending_moves.get(vehicle_id)
            if target_pos is not None:
                blocker = occupied_cells.get(target_pos)
                rospy.logwarn(
                    f"[TrafficController] FORCE CLEARING {target_pos} "
                    f"— freeing {vehicle_id} after {waited:.1f}s wait"
                )
                if blocker and blocker != vehicle_id:
                    if occupied_cells.get(target_pos) == blocker:
                        del occupied_cells[target_pos]
                        del vehicle_positions[blocker] 
                        pending_moves.pop(blocker, None)  
                        waiting_since.pop(blocker, None) 


            waiting_since.pop(vehicle_id, None)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    rospy.init_node('traffic_controller', anonymous=False)

    for vehicle_name in ['vehicle1', 'vehicle2', 'vehicle3']:
        rospy.Subscriber(
            f'/{vehicle_name}/position',
            String,
            parse_position
        )

    rospy.Service('/request_move', RequestMove, handle_move_request)

    rospy.loginfo("========================================")
    rospy.loginfo("  Traffic Controller started!")
    rospy.loginfo("  Listening on /vehicle_position")
    rospy.loginfo("  Serving /request_move")
    rospy.loginfo("========================================")

    rate = rospy.Rate(0.2)  # print grid every 5 seconds
    while not rospy.is_shutdown():
        print_grid()
        with lock:
            check_long_waiters()
        rate.sleep()


if __name__ == "__main__":
    main()