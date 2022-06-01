# Importamos las librerías
from djitellopy import tello
import cv2
import cvzone
from cvzone.FaceDetectionModule import FaceDetector

# Función que ejecutará la funcionalidad en el main.py
def FaceFollowingES():

    # Detectar la cara mediante el objeto FaceDetector
    # objeto detector (Por defecto valor mínimo 0.5) si queremos que sea más preciso debemos subir este a 0.7 o más
    detector = FaceDetector(minDetectionCon=0.6)

    # Márgenes para el video
    hi, wi = 480, 640

    # Los controladores serán para el eje x, el eje y y el eje z para el forward y backward
    # target value es el centro de nuestra imagen
    # como la velocidad no puede ser superada por 100 y con P = 1, nos está devolviendo valores de más de 100
    # no usaremos la I, porque la I es para sistemas muy precisos y muy responsivos
    # D se usa en relación a P, para que reduzca la velocidad según se acerca al centro, para que no vaya
    # rebotando de lado a lado por ir demasiado deprisa
    xPID = cvzone.PID([0.22, 0, 0.1], wi // 2)
    # PID para y
    yPID = cvzone.PID([0.27, 0, 0.1], hi // 2, axis=1)
    # con el límite lo que queremos conseguir es que hacia atrás vaya más lento y hacia delante más deprisa,
    # porque la respuesta yendo hacia detrás es más rápida
    zPID = cvzone.PID([0.005, 0, 0.003], 12000, limit=[-20, 15])

    # definimos nuestro plotter en x
    myPlotX = cvzone.LivePlot(yLimit=[-100, 100], char='X')
    # definimos nuestro plotter en y
    myPlotY = cvzone.LivePlot(yLimit=[-100, 100], char='Y')
    # definimos nuestro plotter en Z
    myPlotZ = cvzone.LivePlot(yLimit=[-100, 100], char='Z')

    # Conectamos con el Tello
    me = tello.Tello()
    me.connect()
    # Imprimimos la batería
    print(me.get_battery())
    # Apagamos la cámara
    me.streamoff()
    # Encendemos la cámara
    me.streamon()

    # Despegamos el dron
    me.takeoff()

    # Lo subimos más alto (80)
    me.move_up(80)

    # Esperamos 1 segundo
    cv2.waitKey(1)

    # Bucle mientras que sea verdadera la obtención de imágenes
    while True:
        # Obtenemos la imagen
        img = me.get_frame_read().frame
        # Resize para que vaya más fluida
        img = cv2.resize(img, (640, 480))
        # encontrar las caras (devuelve la imagen y la bounding box con información de su precisión)
        # le daremos la imagen y un parámetro dónde sabremos si queremos dibujar el dibujo (en este caso true)
        # si solo queremos una cara (bbox) al ser varias caras (bboxs) (por defecto es True)
        img, bboxs = detector.findFaces(img, True)

        # Inicializamos los valores
        xVal = 0
        yVal = 0
        zVal = 0

        # ahora debemos obtener el eje x y el eje y (para encontrar la localización)
        # comprobaremos si hay alguna cara reconocida, es decir sino esta vacío hará esto (buscando el center)
        if bboxs:

            # Tomamos valores de la bbox como son: centro de x y de y
            cx, cy = bboxs[0]['center']
            # por lo que el valor para z será, donde w y h lo obtendremos de nuestro bbox
            x, y, w, h = bboxs[0]['bbox']
            # el área será igual al largo por el ancho de la bbox que rodee a nuestra cara
            area = w * h

            # para controlar que el dron se mantenga siempre en el centro de la imagen, lo que haremos será usar
            # un PID controller, para que la imagen esté estabilizada lo que hará es actualizar al valor actual
            # nuestro cx (el valor a devolver debe ser entero)
            xVal = int(xPID.update(cx))
            # para y será cy
            yVal = int(yPID.update(cy))
            # para z, debemos conseguir como de lejos estamos por lo que podemos hacer es que el área de la cara
            # será más grande si nos acercamos y más pequeño si nos acercamos
            zVal = int(zPID.update(area))

            # mostraremos el plot
            imgPlotX = myPlotX.update(xVal)
            imgPlotY = myPlotY.update(yVal)
            imgPlotZ = myPlotZ.update(zVal)

            # con este método puedes hacerlo para x también para y, pero no puedes hacerlo para z
            # otra forma de verlo visual es con el método draw
            img = xPID.draw(img, [cx, cy])
            img = yPID.draw(img, [cx, cy])

            # lo que ahora necesitamos es visualizarlo en un gráfico por lo que él ploteo el muy importante en PID
            imgStacked = cvzone.stackImages([img, imgPlotX, imgPlotY, imgPlotZ], 2, 0.75)

            # ponemos un texto para ver los valores de z
            cv2.putText(imgStacked, str(area), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 0, 3)
        else:
            imgStacked = cvzone.stackImages([img], 1, 0.75)

        # en z e y los valores están al revés por lo que ponemos en vez de:
        # yVal -> -yVal
        # zVal -> -zVal
        me.send_rc_control(0, -zVal, -yVal, xVal)

        # Se muestra la batería que tiene
        cv2.putText(img, str("Bateria: "), (20, -200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.putText(img, str(me.get_battery()), (40, -200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # Mostramos la imagen que hemos construido
        cv2.imshow("Image Stacked", imgStacked)

        # Si se pulsa q el dron aterriza (es una tecla de emergencia)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            me.land()
            break
    # Si se pulsa q el dron aterriza (es una tecla de emergencia)
    cv2.destroyAllWindows()


# para ejecutar la función en main
if __name__ == '__main__':
    FaceFollowingES()

