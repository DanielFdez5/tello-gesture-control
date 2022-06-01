from djitellopy import tello
import cv2
import cvzone
from cvzone.FaceDetectionModule import FaceDetector

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

# los controladores serán para el eje x, el eje y el otro para el forward y backward
# dara el output como error P(1)I(0)D(0)
# target value es el centro de nuestra imagen
# como la velocidad no puede ser superada por 100 y con P = 1, nos está devolviendo valores de más de 100 lo que haremos
# será modificar P, ahora tomará un valor de 0.3
# no usaremos la I, porque la I es para sistemas muy precisos y muy responsivos
# D se usa en relación a P, para que reduzca la velocidad según se acerca al centro, para que no vaya rebotando de lado a lado
# por ir demasiado deprisa
xPID = cvzone.PID([0.3, 0, 0.1], wi//2)

# definimos nuestro plotter en x
myPlotX = cvzone.LivePlot(yLimit=[-wi // 2, wi // 2], char='X')

""" COMENTAMOS EL DRON PARA TRABAJAR CON LA WEBCAM
PARA NO ESTAR ENCENDIENDOLO Y APAGÁNDOLO!
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamoff()
me.streamon()
"""

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

        # para controlar que el dron se mantenga siempre en el centro de la imagen, lo que haremos será usar
        # un PID controller, para que la imagen esté estabilizada
        # lo que hará es actualizar al valor actual nuestro cx
        # el valor a devolver debe ser entero
        xVal = int(xPID.update(cx))

        # mostraremos el plot
        imgPlotX = myPlotX.update(xVal)

        # con este método puedes hacerlo para x también para y, pero no puedes hacerlo para z
        # otra forma de verlo visual es con el método draw
        img = xPID.draw(img, [cx, cy])

        # lo que ahora necesitamos es visualizarlo en un gráfico por lo que el ploteo el muy importante en PID

    """
        # hay que tener en cuenta que la velocidad de nuestro dron no puede ser mayor a 100, por lo que imprimiremos
        # el valor xVal para saber que valores está devolviendo
        cv2.putText(img, str(xVal), (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        # esta línea nos aparecerá en el centro de nuestra imágen
        cv2.line(img, (wi // 2, 0), (wi // 2, hi), (255, 0, 255), 1)

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
        
    """

    """
    PODEMOS JUNTAR ESTO EN UNA ÚNICA IMAGEN DE LA SIGUIENTE FORMA
    cv2.imshow("Image", img)
    cv2.imshow("PlotX", imgPlotX)
    """
    imgStacked = cvzone.stackImages([img, imgPlotX], 2, 1)
    cv2.imshow("Image Stacked", imgStacked)


    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
