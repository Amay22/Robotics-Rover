import numpy as np


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!
    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        # Check if we've moved the rover sufficiently
        if Rover.pos[0] and Rover.pos[1] and Rover.yaw:
            Rover.sufficient_movement = np.absolute(Rover.recorded_pos[0] - Rover.pos[0]) > 2 or \
                                        np.absolute(Rover.recorded_pos[1] - Rover.pos[1]) > 2 or \
                                        np.absolute(Rover.recorded_pos[2] - Rover.yaw) % 360 > 2
        # check if stock and update the mode
        if ((Rover.vel == 0 and np.absolute(Rover.throttle) > 0) or \
            (Rover.total_time - Rover.recorded_pos[3] > 2 and not Rover.sufficient_movement)) \
            and not Rover.near_sample:
            print("Stuck")
            Rover.mode = 'stuck'
        # Check if we're near a sample
        if Rover.near_sample == 1:
            print("Near sample!")
            Rover.mode = 'stop'

        if Rover.sufficient_movement:
            print("Rover has moved sufficiently")
            Rover.recorded_pos = (Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.total_time)
            # setting sufficient movement to False for next iteration
            Rover.sufficient_movement = False
                                   
        if Rover.mode == 'forward':
            if Rover.ground_pixels_count >= Rover.is_blocked_thresh:
                print("Clear path ahead")
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                if Rover.found_rock:
                    print("Rock Spotted Moving slowly")
                    Rover.throttle = 0.1
            else:
                print("Path is blocked")
                Rover.throttle, Rover.steer, Rover.brake, Rover.mode = 0, 0, Rover.brake_set, 'stop'
        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode or slowing down for a rock but still moving keep braking
            if Rover.vel > 0.2 or Rover.near_sample == 1:
                print("Slowing Down")
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel <= 0.2) then do something else
            else:
                print("Stopped")
                # Now we're stopped and we have vision data to see if there's a path forward
                if Rover.ground_pixels_count < Rover.is_cleared_path_thresh:
                    print("No clear path ahead hence, Rotating to spot clear path")
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                else:
                    print("Path is clear Moving Forward")
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
        elif Rover.mode == 'stuck':
            print("Stuck rotate in place")
            Rover.throttle = 0
            # Release the brake to allow turning
            Rover.brake = 0
            # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
            Rover.steer = -15 # Could be more clever here about which way to turn
            Rover.mode = 'forward'
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        print("Picking up sample")
        Rover.send_pickup = True
    
    return Rover
