# We import the libraries
from djitellopy import tello
import cv2
import cvzone
from cvzone.FaceDetectionModule import FaceDetector

# Function that will execute the functionality in the main.py
def FaceFollowingEN():

    # Detect face using FaceDetector object
    # detector object (Default minimum value 0.5) if we want it to be more accurate we must raise it to 0.7 or more.
    detector = FaceDetector(minDetectionCon=0.6)

    # Video margins
    hi, wi = 480, 640

    # The controllers will be for the x-axis, y-axis and z-axis for forward and backward.
    # target value is the center of our image
    # as the velocity cannot be exceeded by 100 and with P = 1, it is returning values of more than 100
    # we won't use I, because I is for very precise and very responsive systems
    # D is used in relation to P, so that it slows down as it approaches the center, so that it doesn't go
    # bouncing from side to side because it is going too fast
    xPID = cvzone.PID([0.22, 0, 0.1], wi // 2)
    # PID for y
    yPID = cvzone.PID([0.27, 0, 0.1], hi // 2, axis=1)
    # with the limit what we want to achieve is that backwards goes slower and forwards goes faster,
    # because the response going backwards is faster.
    zPID = cvzone.PID([0.005, 0, 0.003], 12000, limit=[-20, 15])

    # we define our plotter in x
    myPlotX = cvzone.LivePlot(yLimit=[-100, 100], char='X')
    # define our plotter in y
    myPlotY = cvzone.LivePlot(yLimit=[-100, 100], char='Y')
    # define our plotter in Z
    myPlotZ = cvzone.LivePlot(yLimit=[-100, 100], char='Z')

    # We connect to the Tello
    me = tello.Tello()
    me.connect()
    # We print the battery
    print(me.get_battery())
    # Turn off the camera
    me.streamoff()
    # Turn on the camera
    me.streamon()

    # We take off the drone
    me.takeoff()

    # We raise it higher (80)
    me.move_up(80)

    # We wait 1 second
    cv2.waitKey(1)

    # Loop as long as true to get images
    while True:
        # We get the image.
        img = me.get_frame_read().frame
        # Resize to make it run smoother
        img = cv2.resize(img, (640, 480))
        # find the faces (returns the image and the bounding box with information about its precision)
        # we will give the image and a parameter where we will know if we want to draw the drawing (in this case true)
        # if we only want a single face (bbox) to be several faces (bboxs) (default is True)
        img, bboxs = detector.findFaces(img, True)

        # Initialize the values
        xVal = 0
        yVal = 0
        zVal = 0

        # now we must get the x-axis and y-axis (to find the location)
        # we will check if there is any recognized face
        # i.e. if it is not empty it will do this (looking for the center)
        if bboxs:

            # we take values from the bbox as are: center of x and y.
            cx, cy = bboxs[0]['center']
            # so the value for z will be, where w and h we will get from our bbox
            x, y, w, h = bboxs[0]['bbox']
            # the area will be equal to the length times the width of the bbox surrounding our face
            area = w * h

            # to control that the drone stays always in the center of the image, what we will do is to use
            # a PID controller, so that the image is stabilized what it will do is to update to the current value
            # our cx (the value to return must be integer)
            xVal = int(xPID.update(cx))
            # for y will be cy
            yVal = int(yPID.update(cy))
            # for z, we must get how far away we are so we can do is that the area of the face
            # will be bigger if we get closer and smaller if we get closer
            zVal = int(zPID.update(area))

            # we will display the plot
            imgPlotX = myPlotX.update(xVal)
            imgPlotY = myPlotY.update(yVal)
            imgPlotZ = myPlotZ.update(zVal)

            # with this method you can do it for x also for y, but you can't do it for z
            # another way to see it visually is with the draw method
            img = xPID.draw(img, [cx, cy])
            img = yPID.draw(img, [cx, cy])

            # what we need now is to visualize it in a graph so the plotting is very important in PID
            imgStacked = cvzone.stackImages([img, imgPlotX, imgPlotY, imgPlotZ], 2, 0.75)

            # we put a text to see the z values
            cv2.putText(imgStacked, str(area), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 0, 3)
        else:
            imgStacked = cvzone.stackImages([img], 1, 0.75)

        # in z and y the values are reversed so we put instead of:
        # yVal -> -yVal
        # zVal -> -zVal
        me.send_rc_control(0, -zVal, -yVal, xVal)

        # The battery you have is displayed
        cv2.putText(img, str("Battery: "), (0, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.putText(img, str(me.get_battery()), (140, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # We show the image we have built
        cv2.imshow("Image Stacked", imgStacked)

        # If q is pressed the drone lands (it's an emergency key)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            me.land()
            break
    # if q is pressed the drone lands (it is an emergency key)
    cv2.destroyAllWindows()


# to execute the function in main
if __name__ == '__main__':
    FaceFollowingEN()

