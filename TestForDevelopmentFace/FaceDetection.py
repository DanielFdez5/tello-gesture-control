from djitellopy import tello
import cv2
from cvzone.FaceDetectionModule import FaceDetector

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamoff()
me.streamon()

# objeto detecto (Por defecto valor mínimo 0.5) si queremos que sea
# mas preciso debemos subir este a 0.7 o más
# min detection
detector = FaceDetector()

while True:
    img = me.get_frame_read().frame
    # encontrar las caras (devuelve la imagen y la bounding box con información de su precisión)
    # le daremos la imagen y un parámetro deonde sabremos si queremos dibujar el dibujo (en este caso true)
    # si solo queremos una cara (bbox) al ser varias caras (bboxs)
    # por defecto es True
    img, bbox = detector.findFaces(img, True)
    cv2.imshow("Image", img)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
