# Program that is able to control the pc keyboard to give commands to the drone.
# Also capture images and save them in the device remotely.

# Import the following libraries:
from djitellopy import tello
import KeyboardControl.KeyPressModule_EN as kpEN
import time
import cv2
1
global image

def KeyboardControlEN():
    # Initialize the module
    kpEN.init()

    # to connect to our tello
    # create the tello object
    dron = tello.Tello()
    # connect to tello
    print("Are we connected?")
    # it must return ok
    dron.connect()

    # We make sure that it goes correctly, for this we print the battery status on screen
    print("Battery status: " + str(dron.get_battery()))

    # Initialize the camera
    dron.streamon()
    print("Camera initialized")

    # Define a function that checks that the key is pressed
    def getKeyboardInputEN():
        # Left&Right -> lr | Forward&Backward -> fb
        # Up&Down -> ud | YourVelocity(Speed) -> yv
        lr, fb, ud, yv = 0, 0, 0, 0
        # Declare a variable for the velocity
        speed = 50

        # If we click on left we move to left
        if kpEN.getKeyEN("LEFT"):
            lr = -speed
        # if kp.getKey("LEFT"): lr = -speed
        if kpEN.getKeyEN("RIGHT"):
            lr = speed

        # If click on top scrolls us forward
        if kpEN.getKeyEN("UP"):
            fb = speed
        # if kp.getKey("UP"): fb = speed
        elif kpEN.getKeyEN("DOWN"):
            fb = -speed

        # W (up), S (down), A (turn left(rotate)), D (turn right(rotate))
        if kpEN.getKeyEN("w"):
            ud = speed
        if kpEN.getKeyEN("s"):
            ud = -speed

        if kpEN.getKeyEN("a"):
            yv = -speed
        if kpEN.getKeyEN("d"):
            yv = speed

        # Q (landing) and "E" (takeoff)
        if kpEN.getKeyEN("q"):
            dron.land()
        if kpEN.getKeyEN("e"):
            dron.takeoff()

        # Take image with space button and save it to the current device.
        if kpEN.getKeyEN("SPACE"):
            tiempo = time.time()
            cv2.imwrite(f"KeyboardControl/saved/{tiempo}.jpg", image)
            print(f"Picture taken")
            time.sleep(0.1)

        return [lr, fb, ud, yv]

    # We make a loop that is continuously watching if we send a key to the loop.
    while True:
        value = getKeyboardInputEN()
        dron.send_rc_control(value[0], value[1], value[2], value[3])

        # As long as True we will get the drone frames.
        image = dron.get_frame_read().frame
        # To process the images faster
        # Para procesar las imágenes más rapido
        image = cv2.resize(image, (640, 480))

        cv2.putText(image, str("Battery:"), (0, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.putText(image, str(dron.get_battery()), (140, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        # we create a window that shows us the images
        cv2.imshow("Image", image)
        # we will give a delay so that the image is not automatically removed before we see it (1 millisecond)
        cv2.waitKey(1)

        time.sleep(0.05)


if __name__ == '__main__':
    KeyboardControlEN()
