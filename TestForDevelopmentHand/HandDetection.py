import cv2
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)

# declaramos el objeto
# el máximo de manos es 1
detector = HandDetector(maxHands=1, minTrackCon=0.7)

while True:

    _, img = cap.read()
    # Detectar las manos de la imagen
    # por defecto dibujará automáticamente
    img = detector.findHands(img)

    # Para detectar los puntos y la bbox será
    # por defecto dibujará automáticamente
    lmList, bboxInfo = detector.findPosition(img)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
