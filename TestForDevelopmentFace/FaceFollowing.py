from djitellopy import tello
import cv2
from cvzone.FaceDetectionModule import FaceDetector

""" COMENTAMOS EL DRON PARA TRABAJAR CON LA WEBCAM
PARA NO ESTAR ENCENDIENDOLO Y APAGÁNDOLO!
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamoff()
me.streamon()
"""

# objeto detecto (Por defecto valor mínimo 0.5) si queremos que sea
# mas preciso debemos subir este a 0.7 o más
# min

cap = cv2.VideoCapture(0)
detector = FaceDetector()

# obtenemos el primer frame para calcular la resolución del vídeo
_, img = cap.read()
# alto, y ancho, el tercer parámetro es el canal (ya que es una imágen a color)
hi, wi, _ = img.shape
print(hi, wi)

while True:
    _, img = cap.read()
    #img = me.get_frame_read().frame
    # encontrar las caras (devuelve la imagen y la bounding box con información de su precisión)
    # le daremos la imagen y un parámetro deonde sabremos si queremos dibujar el dibujo (en este caso true)
    # si solo queremos una cara (bbox) al ser varias caras (bboxs)
    # por defecto es True
    img, bboxs = detector.findFaces(img, True)

    # ahora debemos obtener el eje x y el eje y
    # para encontrar la localización sería
    # comprobaremos si hay alguna cara reconocida, es decir
    # sino esta vacío hará esto
    # para ello buscamos el center
    if bboxs:
        cx, cy = bboxs[0]['center']

        # dibujaremos un círculo en el centro de esta si nos detecta
        # la cara
        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        # ahora lo que queremos es saber como de lejos esta el centro
        # de la imagen de nuestro centro
        # esta línea nos aparecerá en el centro de nuestra imágen
        cv2.line(img, (wi//2, 0), (wi//2, hi), (255, 0, 255), 1)

        # ahora lo que queremos es la distancia entre nuestra linea y exposición de nuestra cara
        error = wi // 2 - cx
        cv2.putText(img, str(error), (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        # para ver esta distancia con una línea lo haremos de la siguiente forma
        cv2.line(img, (wi//2, hi//2), (cx, cy), (255, 0, 255), 3)

    cv2.imshow("Image", img)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
