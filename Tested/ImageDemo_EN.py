from djitellopy import tello
import cv2

def ImageDemoEN():
    # we create the object
    me = tello.Tello()
    # connect the drone
    me.connect()
    # print the battery percentage
    print(me.get_battery())

    # turn off the camera
    me.streamoff()
    # turn on the camera
    me.streamon()

    # as long as True...
    while True:
        # this gives us the drone camera image.
        img = me.get_frame_read().frame
        # resets it to 640x480
        img = cv2.resize(img, (640, 480))
        # show it with the name Image
        cv2.imshow("Image", img)

        # if you press the q button it will be turned off
        if cv2.waitKey(5) & 0xFF == ord('q'):  # 5 milliseconds
            me.streamoff()
            break

        print("Camera running!")
        # we wait
        cv2.waitKey(5000)
        print("Test done!")
        # we wait
        cv2.waitKey(2000)
        print("You are going to be disconnected...")
        # we wait
        cv2.waitKey(2000)
        # we disconnect
        me.streamoff()
        # destroy the window that has been opened with the image
        cv2.destroyAllWindows()
        break

    # disconnect...
    print("Disconnecting...")
    print("")
    print("")


if __name__ == '__main__':
    ImageDemoEN()
