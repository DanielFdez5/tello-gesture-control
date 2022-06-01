# We import the libraries
from cvzone.PoseModule import PoseDetector
import cv2
import time
from djitellopy import tello
import cvzone

# Function that will execute the functionality in the main.py
def BodyGestureDetectionEN():

    # Detect body using PoseDetector object.
    # upBody to detect the upper part of the body only
    # detectionCon (0 - 1): Detection accuracy
    # trackCon (0 - 1): reference point tracking
    detector = PoseDetector(upBody=True, detectionCon=0.6, trackCon=0.6)

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
    zPID = cvzone.PID([0.00016, 0, 0.00011], 150000, limit=[-20, 30])

    # We will create a timer for the selfie
    snapTimer = 0

    # Variable that will store a boolean to activate or deactivate the TrackingMode
    trackingMode = False

    # we establish a color for each gesture to differentiate it from others
    colorGesture = (0, 0, 255)

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

    # We save here the movements
    gesture = ''

    # Loop as long as the imaging is true
    while True:

        # We get the image
        img = me.get_frame_read().frame
        # Resize to make it run smoother
        img = cv2.resize(img, (640, 480))

        # Now what we have to do is to get the points through findPose (we can erase
        # the drawing by setting draw = False)
        img = detector.findPose(img)
        # We will save the information of the points in lmlist (landmarks) and of the bbox in bboxInfo
        lmList, bboxInfo = detector.findPosition(img)

        # We initialize the values:
        # These values send the distance the drone has to travel to reposition itself correctly.
        xVal = 0
        yVal = 0
        zVal = 0

        # We add a condition to avoid an error if there is no image do not process the angle.
        if bboxInfo:

            # We take values from the bbox such as: center of x and center of y
            cx, cy = bboxInfo['center']
            # From the bonding box we take x and width and length
            x, y, w, h = bboxInfo['bbox']
            # the area will be equal to the length times the width of the bbox surrounding our body
            area = w * h

            # to control that the drone stays always in the center of the image, what we will do is to use
            # a PID controller, so that the image is stabilized
            xVal = int(xPID.update(cx))
            yVal = int(yPID.update(cy))
            zVal = int(zPID.update(area))

            # first we will make the left arm (angle)
            # make sure that the middle point is p2, the ends are indifferent.
            # if we put the points upside down what will happen is that the angle will go from 360 to less
            # if we don't want to see the angles, we only have to set draw = False (default is True)
            angArmL = detector.findAngle(img, 13, 11, 23)
            # now we will make the right arm (angle)
            angArmR = detector.findAngle(img, 14, 12, 24)

            # to make the crossed arms pose we need to calculate
            # as in this case the hands will be glued to our shoulders
            # we need to calculate the distance from our hands to our shoulders
            # we will go to the points and what we have to do is when the marking
            # 15 is close to 12 and 16 is close to 11 then you will recognize that the # arms are crossed.
            # arms are crossed, another condition that we could add is the angles.
            # this will be evaluated later
            distArmL, img, _ = detector.findDistance(15, 12, img)
            distArmR, img, _ = detector.findDistance(16, 11, img)

            # what it will do is to check that the angle obtained is similar and approximate to 90,
            # if it is true it returns TRUE, if it is false it returns FALSE
            # we can define a minimum and a maximum by default this value is 20
            # checkTposeL and checkTposeR will be used to check the angle of the position T
            checkTposeL = detector.angleCheck(angArmL, 90)
            checkTposeR = detector.angleCheck(angArmR, 270)
            # checkUpPoseL and checkUpPoseR will be used to check the angle of both raised arms.
            checkUpPoseL = detector.angleCheck(angArmL, 180)
            checkUpPoseR = detector.angleCheck(angArmR, 180)

            # If the angle is correct, it means that the position of T is being performed.
            if checkTposeL and checkTposeR:
                # gesture is saved for display on screen
                gesture = 'T pose'
                # for T position we will stop the drone to stop tracking us
                trackingMode = False

            # if the angle is correct it means that the arms up position is being performed
            elif checkUpPoseL and checkUpPoseR:
                # the gesture is saved for displaying on the screen
                # Tracking Mode
                gesture = 'Arms up'  # green color
                # the drone will start tracking us
                trackingMode = True

            # first we will check if there is distance and if there is it will enter the condition
            elif distArmL and distArmR:
                # for this we will check that if the position of t is less than 100 then.
                # recognizes it as valid, if it is valid it means that we are crossing our arms.
                if distArmL < 100 and distArmR < 100:
                    # the gesture is saved for display on screen.
                    gesture = "Arms crossed"

                    # so if the arms are crossed and it's correct, we proceed to take a picture, so
                    # the timer will start at 3 towards 0 to take the picture
                    # i.e. 3,2,1 selfi!
                    snapTimer = time.time()

            # if our timer is greater than 0 it means that some action will happen
            if snapTimer > 0:
                # what we will do is calculate current time minus timer to know the seconds elapsed.
                totalTime = time.time()-snapTimer

                # we don't put = because there are times when the timer jumps by milliseconds and it can
                # skip this number so we will work with major and minor
                # If it has passed between 0 and 0.9 we'll put 3 (backward timer)
                if 0 < totalTime < 0.9:
                    # write to screen 3
                    cv2.putText(img, "3", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                # If it has passed between 1 and 1.9 we will put 2
                elif 1 < totalTime < 1.9:
                    # write to screen 2
                    cv2.putText(img, "2", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                # If it has passed between 2 and 2.9 we will put 1
                elif 2 < totalTime < 2.9:
                    # write to screen 1
                    cv2.putText(img, "1", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                # Once the 3 seconds have elapsed we will take the photo
                elif totalTime > 3:
                    # We save the picture in the folder saved.
                    # The picture is saved over time because it is the only way not to overwrite it with the
                    # same name
                    cv2.imwrite(f'BodyGestureDetection/saved/{time.time()}.jpg', img)
                    # reset the timer to 0 so that after finishing the action it is not in a continuous loop
                    snapTimer = 0
                    # write to screen "selfie!"
                    cv2.putText(img, "selfi!", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 0), 5)
                    # wait 0.2 seconds
                    time.sleep(0.2)
            else:
                # writes to the screen the gesture being performed.
                cv2.putText(img, gesture, (5, 40), cv2.FONT_HERSHEY_PLAIN, 2, colorGesture, 2)

            # in case tracking mode is activated this conditional will be entered
            if trackingMode:
                # send movements to the drone to perform, send it:
                # zval is forward and backward (0, zval, 0, 0, 0)
                # yval is up and down (0, 0, yval, 0)
                # xval is Right and Left (0, 0, 0, 0, xval)
                me.send_rc_control(0, -zVal, -yVal, xVal)
                # We show Follow in the drone
                cv2.putText(img, "Follow!", (480, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            else:
                # tracking is stopped, so the drone must be stopped (0, 0, 0, 0, 0).
                me.send_rc_control(0, 0, 0, 0)
                # We show Follow in the drone
                cv2.putText(img, "No follow!", (400, 40), cv2.FONT_HERSHEY_PLAIN, 2, colorGesture, 2)

        # The battery you have is shown
        cv2.putText(img, str("Battery: "), (0, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.putText(img, str(me.get_battery()), (140, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # we show the image
        cv2.imshow("Image", img)
        # We wait
        cv2.waitKey(1)

        # If q is pressed the drone lands (it is an emergency key)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            me.land()
            break

    # Destroy the windows to close the functionality correctly
    cv2.destroyAllWindows()


# To execute function in main.py
if __name__ == '__main__':
    BodyGestureDetectionEN()
