import cv2
from cvzone.PoseModule import PoseDetector

# Inicializamos el objeto
# detect & tracking
#detector = PoseDetector()
detector = PoseDetector()

# captamos la videocamara
cap = cv2.VideoCapture(0)

# Bucle mientres detecte nuestro cuerpo
while True:
    # obtenemos el frame
    _, img = cap.read()
    # lo enviamos a detector, para encontrar la pose
    img = detector.findPose(img)
    # obtendremos los puntos, esto devolverá la lista de puntos, y la bbox information
    # en caso de querer que nuestro area se modifique cuando hagamos gestos, debemos
    # bboxWithHands = true

    # lmlist, bboxInfo = detector.findPosition(img, bboxWithHands=True)
    # hay veces que no queremos que dibuje entero o si estemos lejos nos dibuje, para ello hay una
    # opcion detector = PoseDetector(upBody=True) entonces solo dibujaría con la bbox de la parte superior
    # hacia arriba de esta forma el frame será más consistente ya que no estará cambiando de tamaño tod0
    # el rato
    lmlist, bboxInfo = detector.findPosition(img)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
