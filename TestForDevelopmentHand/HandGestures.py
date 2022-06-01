import cv2
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)

# declaramos el objeto
# el máximo de manos es 1
detector = HandDetector(maxHands=1)
contador = 0

while True:

    _, img = cap.read()
    # Detectar las manos de la imagen
    # por defecto dibujará automáticamente
    img = detector.findHands(img)

    # Para detectar los puntos y la bbox será
    # por defecto dibujará automáticamente
    lmList, bboxInfo = detector.findPosition(img)

    if bboxInfo:
        # contaremos el número de dedos levantados
        nFingers = detector.fingersUp()
        #print(nFingers)

        # contaremos el número de dedos a través de la obtención de cada dedo
        # thumb, index, middle, ring, pinky = detector.fingersUp()

        # esta forma es un poco mala, en el sentido de la cantidad de variables que ponemos
        """
        if thumb and index and middle and ring and pinky:
            print("Open hand")
        elif not thumb and not index and not middle and not ring and not pinky:
            print("Close hand")
        elif not thumb and index and not middle and not ring and not pinky:
            print("Index")
        """
        # otra forma sería
        # como vemos reducimos la complejidad y el número de parámetros
        if nFingers == [1, 1, 1, 1, 1]:
            print("Open hand")
        elif nFingers == [0, 0, 0, 0, 0]:
            print("Close hand")
        elif nFingers == [0, 1, 0, 0, 0]:
            print("Index")
        elif nFingers == [0, 1, 0, 0, 1]:
            print("Rock pose")

    cv2.imshow("Image", img)
    cv2.waitKey(1)
