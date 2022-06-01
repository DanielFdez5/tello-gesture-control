from djitellopy import tello
import time
import cv2

def FlyingDemoEN():

    # Object to import tello
    me = tello.Tello()
    # we connect with tello
    me.connect()
    # we get the percentage of the battery
    print(me.get_battery())

    # fly drone
    me.takeoff()

    # we will move up drone far away than by default
    # we can write too as me.move('up', 80)
    # move with distance
    me.move_up(80) # 80 cm

    # to move the drone you don't tell it to go and move 50 cm.
    # if you don't change its speed until you get to that point
    # range from -100 to 100
    # 1 -> left_right
    # 2 -> forward, backward
    # 3 -> up, down
    # 4 -> yaw
    # move with speed

    # Testing left
    print("Testing left")
    me.send_rc_control(-20, 0, 0, 0)
    print("Test done")
    time.sleep(1)  # 1 seconds

    # Testing right
    print("Testing right")
    me.send_rc_control(20, 0, 0, 0)
    print("Test done")
    time.sleep(1)  # 1 seconds

    # Testing forward
    print("Testing forward")
    me.send_rc_control(0, 20, 0, 0)
    print("Test done")
    time.sleep(1)  # 1 seconds

    # Testing backward
    print("Testing backward")
    me.send_rc_control(0, -20, 0, 0)
    print("Test done")
    time.sleep(1)  # 1 seconds

    # Testing up
    print("Testing up")
    me.send_rc_control(0, 0, 20, 0)
    print("Test done")
    time.sleep(1)  # 1 seconds

    # Testing down
    print("Testing down")
    me.send_rc_control(0, 0, -20, 0)
    print("Test done")
    time.sleep(1)  # 1 seconds

    # Testing left rotation
    print("Testing left rotation")
    me.send_rc_control(0, 0, 0, -90)
    print("Test done")
    time.sleep(1)  # 1 seconds

    # Testing right rotation
    print("Testing right rotation")
    me.send_rc_control(0, 0, 0, 90)
    print("Test done")
    time.sleep(1)  # 1 seconds

    # Now we will give a speed in a time
    time.sleep(1)  # 1 seconds

    # Make sure the drone is stopped
    me.send_rc_control(0, 0, 0, 0)

    # We land it
    me.land()

    # We wait
    cv2.waitKey(5000)
    print("Test done!")
    # We wait
    cv2.waitKey(2000)
    print("You are going to be disconnected...")
    cv2.waitKey(2000)
    print("")
    print("")
    print("")


if __name__ == '__main__':
    FlyingDemoEN()
