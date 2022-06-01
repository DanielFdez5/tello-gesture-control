from djitellopy import tello
import cv2

def TestedConnectionEN():
    # objects to import tello
    me = tello.Tello()
    # connect our tello
    me.connect()
    print("Connected!")
    print("Battery: ")
    # Battery level
    print(me.get_battery())
    # we wait
    cv2.waitKey(5000)
    print("Test done!")
    # we wait
    cv2.waitKey(2000)
    print("You are going to be disconnected...")
    # we wait
    cv2.waitKey(2000)
    print("")
    print("")
    print("")

if __name__ == '__main__':
    TestedConnectionEN()
