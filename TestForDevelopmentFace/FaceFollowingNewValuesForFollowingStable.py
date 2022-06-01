from djitellopy import tello
import cv2
import cvzone
from cvzone.FaceDetectionModule import FaceDetector

# objeto detecto (Por defecto valor mínimo 0.5) si queremos que sea
# mas preciso debemos subir este a 0.7 o más
# min

# cap = cv2.VideoCapture(0)
detector = FaceDetector(minDetectionCon=0.5)

# obtenemos el primer frame para calcular la resolución del vídeo
# _, img = cap.read()
# alto, y ancho, el tercer parámetro es el canal (ya que es una imágen a color)
# hi, wi, _ = img.shape
# para el dron
hi, wi = 480, 640
# print(hi, wi)

# los controladores serán para el eje x, el eje y el otro para el forward y backward
# dara el output como error P(1)I(0)D(0)
# target value es el centro de nuestra imagen
# como la velocidad no puede ser superada por 100 y con P = 1, nos está devolviendo valores de más de 100 lo que haremos
# será modificar P, ahora tomará un valor de 0.3
# no usaremos la I, porque la I es para sistemas muy precisos y muy responsivos
# D se usa en relación a P, para que reduzca la velocidad según se acerca al centro, para que no vaya rebotando de lado a lado
# por ir demasiado deprisa
xPID = cvzone.PID([0.22, 0, 0.1], wi // 2)
# PID para y
yPID = cvzone.PID([0.27, 0, 0.1], hi // 2, axis=1)
# PID para z, en z no podremos dibujar por lo que quitaremos el eje
# para conseguir z debemos conseguir un valor que calcularemos más adelante
# con el límite lo que queremos conseguir es que hacia atrás vaya más lento y hacia delante más deprisa, porque la respuesta yendo hacia detrás
# es más rápida
zPID = cvzone.PID([0.005, 0, 0.003], 12000, limit=[-20, 15])

# definimos nuestro plotter en x
myPlotX = cvzone.LivePlot(yLimit=[-100, 100], char='X')
# definimos nuestro plotter en y
myPlotY = cvzone.LivePlot(yLimit=[-100, 100], char='Y')
# definimos nuestro plotter en Z
myPlotZ = cvzone.LivePlot(yLimit=[-100, 100], char='Z')

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamoff()
me.streamon()
me.takeoff()
me.move_up(80)
cv2.waitKey(1)

while True:
    # _, img = cap.read()
    img = me.get_frame_read().frame
    # nos aseguramos que la resolución de la imagen es la misma
    img = cv2.resize(img, (640, 480))
    # encontrar las caras (devuelve la imagen y la bounding box con información de su precisión)
    # le daremos la imagen y un parámetro deonde sabremos si queremos dibujar el dibujo (en este caso true)
    # si solo queremos una cara (bbox) al ser varias caras (bboxs)
    # por defecto es True
    img, bboxs = detector.findFaces(img, True)

    xVal = 0
    yVal = 0
    zVal = 0

    # ahora debemos obtener el eje x y el eje y
    # para encontrar la localización sería
    # comprobaremos si hay alguna cara reconocida, es decir
    # sino esta vacío hará esto
    # para ello buscamos el center
    if bboxs:
        cx, cy = bboxs[0]['center']

        # por lo que el valor para z será, donde w y h lo obtendremos de nuestro bbox
        x, y, w, h = bboxs[0]['bbox']
        area = w * h
        # el valor 0 de este área deberá ser definido con el dron, cuando tengamos algo pensado y sea lo más
        # correcto para la detección de nuestra cara respecto al dron

        # para controlar que el dron se mantenga siempre en el centro de la imagen, lo que haremos será usar
        # un PID controller, para que la imagen esté estabilizada
        # lo que hará es actualizar al valor actual nuestro cx
        # el valor a devolver debe ser entero
        xVal = int(xPID.update(cx))
        # para y:
        yVal = int(yPID.update(cy))
        # para z, debemos conseguir como de lejos estamos por lo que podemos hacer es que el área de la cara será
        # más grande si nos acercamos y más pequeño si nos acercamos
        zVal = int(zPID.update(area))
        print(zVal)

        # mostraremos el plot
        imgPlotX = myPlotX.update(xVal)
        imgPlotY = myPlotY.update(yVal)
        imgPlotZ = myPlotZ.update(zVal)

        # con este método puedes hacerlo para x también para y, pero no puedes hacerlo para z
        # otra forma de verlo visual es con el método draw
        img = xPID.draw(img, [cx, cy])
        img = yPID.draw(img, [cx, cy])

        # lo que ahora necesitamos es visualizarlo en un gráfico por lo que el ploteo el muy importante en PID

        imgStacked = cvzone.stackImages([img, imgPlotX, imgPlotY, imgPlotZ], 2, 0.75)
        #imgStacked = cvzone.stackImages([img], 1, 1)
        # ponemos un texto para ver los valores de z
        cv2.putText(imgStacked, str(area), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 0, 3)
        #me.send_rc_control(0, -zVal, -yVal, xVal)
        # Mejor iremos probando los valores uno por uno para asegurarnos de su correcto funcionamiento
    else:
        imgStacked = cvzone.stackImages([img], 1, 0.75)

    #me.send_rc_control(0, 0, 0, xVal)
    # en y los valores estan al reves por lo que ponemos en vez de yVal -> -yVal
    #me.send_rc_control(0, 0, -yVal, 0)
    me.send_rc_control(0, -zVal, -yVal, xVal)
    cv2.waitKey(1)
    cv2.imshow("Image Stacked", imgStacked)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        me.land()
        break

cv2.destroyAllWindows()
