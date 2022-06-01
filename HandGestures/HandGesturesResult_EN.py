# We import the libraries
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
from cvzone.FaceDetectionModule import FaceDetector
import time
from djitellopy import tello

# Function that will execute the functionality in the main.py
def HandGesturesEN():
    # Detect hand using the HandDetector object
    # maxHands: maximum number of hands (default 2)
    # detectionCon (0 - 1): Detection accuracy
    # trackCon (0 - 1): reference point tracking
    detector = HandDetector(maxHands=1, detectionCon=0.9, minTrackCon=0.9)

    # Detect face using FaceDetector object
    # detector object (Default minimum value 0.5) if we want it to be more accurate we must raise it to 0.7 or more.
    detectorFace = FaceDetector(minDetectionCon=0.6)

    # We will create a timer for the selfie
    snapTimer = 0

    # We set a color for the gestures
    colorGesture = (0, 0, 255)

    # Variable to store the gestures
    gesture = ''

    # Initialize the timer
    timer = time.time()

    # We initialize the variable that will identify if we are being tracked or not (default False)
    seguimiento = False

    # Video margins
    hi, wi = 480, 640

    # PID to drive the drone
    # the controllers will be for x-axis, y-axis, z-axis
    # the target value is the center of our image
    # as the velocity can't be more than 100 and with P = 1, it is returning values of more than 100
    # what we will do is to modify P until we get values between -100 and 100
    # we will not use I, because I is for very precise and very responsive systems -> 0
    # D is used in relation to P, so that it slows down as it approaches the center, so that it does not go
    # bouncing from side to side because it is going too fast
    xPID = cvzone.PID([0.22, 0, 0.1], wi // 2)
    yPID = cvzone.PID([0.27, 0, 0.1], hi // 2, axis=1)
    zPID = cvzone.PID([0.005, 0, 0.003], 12000, limit=[-20, 30])

    # We connect with Tello
    me = tello.Tello()
    me.connect()
    # We print the battery
    print(me.get_battery())
    # We turn off the camera
    me.streamoff()
    # we turn on
    me.streamon()

    # We take off the drone
    me.takeoff()

    # We raise it higher (80)
    me.move_up(80)

    # Loop as long as the imaging is true
    while True:

        # We get the image
        img = me.get_frame_read().frame
        # Resize to make it run smoother
        img = cv2.resize(img, (640, 480))

        # Now what we must do is to get the points through findHands(we can erase
        # the drawing by setting draw = False)
        img = detector.findHands(img)
        # We will save the information of the points in lmlist (landmarks) and of the bbox in bboxInfo
        lmList, bboxInfo = detector.findPosition(img)

        # Now what we have to do is to get the face by findFaces (we can delete the drawing by setting draw = False).
        # the drawing by setting draw = False)
        imf, bboxs = detectorFace.findFaces(img, draw=True)

        # We initialize the values:
        # These values send the distance the drone has to travel to reposition itself correctly.
        xVal = 0
        yVal = 0
        zVal = 0

        # We add a condition to avoid an error if there is no image
        if bboxs:

            # From the bonding box we take x and width and length
            x, y, w, h = bboxs[0]["bbox"]
            # We take values from the bbox such as: center of x and center of y
            cx, cy = bboxs[0]['center']
            # the area will be equal to the length times the width of the bbox surrounding our face
            area = w * h

            # to control that the drone stays always in the center of the image, what we will do is to use
            # a PID controller, so that the image is stabilized
            xVal = int(xPID.update(cx))
            yVal = int(yPID.update(cy))
            zVal = int(zPID.update(area))

            # therefore we will create a detection region to detect the hand, and
            # so that it does not constantly detect the movements of the hand, but in a specific area,
            # in this case near the face
            bboxRegion = x -175-50, y -75, 175, h+75

            # once the region is defined, we will draw it in this case, it will be interactive.
            # if there is no hand it will appear in red color and if there is one it will appear in green color
            cvzone.cornerRect(img, bboxRegion, rt=0, t=10, colorC=(0, 0, 255))

            # Now what we will do is to detect if the right hand is in the region or not
            # and if from this, it is detecting the fingers
            # We have to make sure that the hand is "Right".
            if lmList and detector.handType() == "Right":

                # Therefore what we will do is find the center
                handCenter = bboxInfo["center"]

                # once we have the center we can check if it is in the region.
                # inside is True or False and will return whether it is inside or not
                            # x         center x        (x+w)
                            # y         center y        (y+h)
                inside = bboxRegion[0] < handCenter[0] < (bboxRegion[0]+bboxRegion[2]) and \
                         bboxRegion[1] < handCenter[1] < (bboxRegion[1] + bboxRegion[3])

                # if inside is true, we will draw the region in green simulating that it is inside and it is correct
                if inside:
                    # we draw the region in green
                    cvzone.cornerRect(img, bboxRegion, rt=0, t=10, colorC=(0, 255, 0))

                    # We will count the number of fingers raised to be able to interpret the movements,
                    # since the fingers are counted as follows:
                    # raised: 1
                    # not raised: 0
                    nFingers = detector.fingersUp()

                    # We will count the number of fingers through the fetching of each finger.
                    # thumb, index, middle, ring, pinky = detector.fingersUp()
                    # as we can see we reduce the complexity and the number of parameters

                    # if the palm is up then:
                    # gesture = "Stop!", the timer returns to 0 and stops tracking the user.
                    if nFingers == [1, 1, 1, 1, 1]:

                        # We save the gesture Stop!
                        gesture = 'Stop!'
                        # Reset counter
                        timer = time.time()
                        # Set tracking to False
                        seguimiento = False

                    # If the thumb, index finger and little finger are raised
                    # Gesture = "Selfie!", the timer returns to 0, the selfie timer is initialized
                    # and stops following the user.
                    elif nFingers == [1, 1, 0, 0, 1]:

                        # We save the gesture Selfie!
                        gesture = 'Selfie!'
                        # we proceed to take a picture, so the timer will start at 3 towards 0
                        # to take the picture
                        snapTimer = time.time()
                        # we reset the timer
                        timer = time.time()
                        # We set the tracking to False
                        seguimiento = False

                    # If the index, middle and ring finger are raised
                    # Gesture = "Follow!", the follower is initialized.
                    elif nFingers == [0, 1, 1, 1, 0]:
                        # We save the gesture Follow!
                        gesture = 'Follow!'
                        # Set tracking to True
                        seguimiento = True

                    # If the index is raised
                    # Gesture = "Up!", the drone moves up, the timer returns to 0
                    # and stops tracking
                    elif nFingers == [0, 1, 0, 0, 0]:
                        # We save the gesture Up!
                        gesture = 'Go up!'
                        # The drone moves 20 upwards
                        me.send_rc_control(0, 0, 20, 0)
                        # We reset the counter
                        timer = time.time()
                        # Set tracking to False
                        seguimiento = False

                    # If the thumb is raised
                    # Gesture = "Down!", the drone moves down, the timer returns to 0
                    # and stops tracking
                    elif nFingers == [1, 0, 0, 0, 0]:
                        # We save the gesture Down!
                        gesture = 'Go down!'
                        # Drone moves 20 downwards
                        me.send_rc_control(0, 0, -20, 0)
                        # We reset the counter
                        timer = time.time()
                        # Set tracking to False
                        seguimiento = False

                    # If the index and heart are raised
                    # Gesture = "Right!", the drone moves to the right, the timer returns to 0
                    # and stops tracking
                    elif nFingers == [0, 1, 1, 0, 0]:
                        # We save the gesture Right!
                        gesture = 'Go right!'
                        # The drone moves 20 to the right
                        me.send_rc_control(20, 0, 0, 0)
                        # We reset the counter
                        timer = time.time()
                        # Set tracking to False
                        seguimiento = False

                    # If the thumb and little finger are raised
                    # Gesture = "Down!", the drone moves down, the timer returns to 0
                    # and stops tracking
                    elif nFingers == [1, 0, 0, 0, 1]:
                        # We save the gesture Left!
                        gesture = 'Go left!'
                        # The drone moves 20 to the left
                        me.send_rc_control(-20, 0, 0, 0)
                        # We reset the counter
                        timer = time.time()
                        # Set tracking to False
                        seguimiento = False

                    # The words shown in the region are decorated just below it in a green color
                    cv2.rectangle(img, (bboxRegion[0], bboxRegion[1] + bboxRegion[3] + 10),
                                  (bboxRegion[0] + bboxRegion[2], bboxRegion[1] + bboxRegion[3]+60),
                                  (0,255,0), cv2.FILLED)

                    # What we will do is to show on the screen what is being recognized at that moment.
                    cv2.putText(img, f'{gesture}',
                                (bboxRegion[0]+10, bboxRegion[1] + bboxRegion[3] + 50),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

            # if our timer is greater than 0 it means that some action is going to happen
            # in this case the associated action is to take a snapshot.
            if snapTimer > 0:

                # What we'll do is calculate current time minus timer to know the seconds elapsed
                totalTime = time.time() - snapTimer

                # we don't put = because there are times when the timer jumps by milliseconds and it can
                # skip this number so we will work with major and minor
                # If it has passed between 0 and 0.9 we will put 3 (backward timer)
                if 0 < totalTime < 0.9:
                    cv2.putText(img, "3", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                # If it has passed between 1 and 1.9 we will put 2
                elif 1 < totalTime < 1.9:
                    # type on screen 2
                    cv2.putText(img, "2", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                # If it has passed between 2 and 2.9 we will put 1
                elif 2 < totalTime < 2.9:
                    # write to screen 1
                    cv2.putText(img, "1", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                # Once the 3 seconds have elapsed we will take the picture
                elif totalTime > 3:
                    # We save the picture in the folder saved.
                    # The picture is saved over time because it is the only way not to overwrite with the
                    # same name
                    cv2.imwrite(f'HandGestures/saved/{time.time()}.jpg', img)

                    # reset the timer to 0 so that after the action is finished it is not in a continuous loop
                    snapTimer = 0
                    # write to screen "selfie!"
                    cv2.putText(img, "selfie!", (650, 400), cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 0), 5)
                    # wait 0.2 seconds
                    time.sleep(0.2)
            else:
                # Writes on the screen the gesture that is being performed
                cv2.putText(img, gesture, (5, 40), cv2.FONT_HERSHEY_PLAIN, 2, colorGesture, 2)

            # if our timer is greater than 0 it means that some action will happen
            # in this case the associated action is to start tracking after 7 seconds
            # if in 7 seconds there has been no action it starts tracking automatically
            if timer > 0:
                # what we will do is to calculate current time minus timer to know the seconds elapsed.
                totalTime = time.time() - timer
                # Once 7 seconds have elapsed, tracking starts
                if totalTime > 7:
                    # we will reset the timer to 0 so that after finishing the action it is not in a continuous loop.
                    timer = 0
                    # we wait 0.2 seconds
                    time.sleep(0.2)
                    # we set the tracking to True
                    seguimiento = True

            # The battery you have is shown
            cv2.putText(img, str("Battery: "), (0, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            cv2.putText(img, str(me.get_battery()), (140, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            # If tracking is true, the drone starts to follow you.
            if seguimiento:
                # send movements to the drone to perform, send it:
                # zval is Forward and backward (0, zval, 0, 0, 0).
                # yval is up and down (0, 0, yval, 0)
                # xval is Right and Left (0, 0, 0, 0, xval)
                me.send_rc_control(0, -zVal, -yVal, xVal)
                # the drone is shown to be following
                cv2.putText(img, "Following!", (460, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            # If tracking is false the drone will stop following you
            else:
                # tracking is stopped, so the drone must be stopped (0, 0, 0, 0, 0).
                me.send_rc_control(0, 0, 0, 0)
                # shows that the drone is not tracking.
                cv2.putText(img, "Not following!", (400, 40), cv2.FONT_HERSHEY_PLAIN, 2, colorGesture, 2)

        # We show the image
        cv2.imshow("Image", img)
        # We wait
        cv2.waitKey(1)


# To execute the function in main.py
if __name__ == '__main__':
    HandGesturesEN()
