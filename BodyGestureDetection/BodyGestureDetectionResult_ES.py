# Importamos las librerías
from cvzone.PoseModule import PoseDetector
import cv2
import time
from djitellopy import tello
import cvzone

# Función que ejecutará la funcionalidad en el main.py
def BodyGestureDetectionES():

    # Detectar el cuerpo mediante el objeto PoseDetector
    # upBody para detectar la parte superior del cuerpo únicamente
    # detectionCon (0 - 1): Precisión de detección
    # trackCon (0 - 1): seguimientos puntos de referencia
    detector = PoseDetector(upBody=True, detectionCon=0.6, trackCon=0.6)

    # Márgenes vídeos
    hi, wi = 480, 640

    # PID para manejar el dron
    # los controladores serán para el eje x, el eje y, el eje z
    # el target value (objetivo) es el centro de nuestra imagen
    # como la velocidad no puede ser superada por 100 y con P = 1, nos está devolviendo valores de más de 100
    # lo que haremos será modificar ir modificando P hasta que valores comprendidos entre -100 y 100
    # no usaremos la I, porque la I es para sistemas muy precisos y muy responsivos -> 0
    # D se usa en relación a P, para que reduzca la velocidad según se acerca al centro, para que no vaya
    # rebotando de lado a lado por ir demasiado deprisa
    xPID = cvzone.PID([0.22, 0, 0.1], wi // 2)
    yPID = cvzone.PID([0.27, 0, 0.1], hi // 2, axis=1)
    zPID = cvzone.PID([0.00016, 0, 0.00011], 150000, limit=[-20, 30])

    # Crearemos un temporizador para el selfie
    snapTimer = 0

    # Variable que guardará un booleano para activar o desactivar el TrackingMode
    trackingMode = False

    # establecemos un color para cada gesto para que sea diferenciador
    colorGesture = (0, 0, 255)

    # Conectamos con el Tello
    me = tello.Tello()
    me.connect()
    # Imprimimos la batería
    print(me.get_battery())
    # Apagamos la cámara
    me.streamoff()
    # La encendemos
    me.streamon()

    # Despegamos el dron
    me.takeoff()

    # Lo subimos más alto (80)
    me.move_up(80)

    # guardaremos aquí los movimientos
    gesture = ''

    # Bucle mientras que sea verdadera la obtención de imágenes
    while True:

        # Obtenemos la imagen
        img = me.get_frame_read().frame
        # Resize para que vaya más fluido
        img = cv2.resize(img, (640, 480))

        # Ahora lo que debemos hacer es conseguir los puntos a través de findPose(podemos borrar
        # el dibujo poniendo draw = False)
        img = detector.findPose(img)
        # Guardaremos la información de los puntos en lmlist (landmarks) y de la bbox en bboxInfo
        lmList, bboxInfo = detector.findPosition(img)

        # Inicializamos los valores:
        # Dichos valores envían la distancia que tiene que recorrer el dron para reposicionarse de manera correcta
        xVal = 0
        yVal = 0
        zVal = 0

        # Añadimos una condición para evitar un error si no hay imagen no proceses el ángulo
        if bboxInfo:

            # Tomamos valores de la bbox como son: centro de x y de y
            cx, cy = bboxInfo['center']
            # De la bonding box tomamos x y ancho y largo
            x, y, w, h = bboxInfo['bbox']
            # el área será igual al largo por el ancho de la bbox que rodee a nuestro cuerpo
            area = w * h

            # para controlar que el dron se mantenga siempre en el centro de la imagen, lo que haremos será usar
            # un PID controller, para que la imagen esté estabilizada
            xVal = int(xPID.update(cx))
            yVal = int(yPID.update(cy))
            zVal = int(zPID.update(area))

            # primero haremos el brazo izquierdo (ángulo)
            # hay que asegurarse que el punto del medio sea el p2, los extremos son indiferentes
            # si ponemos los puntos al revés lo que pasará es que el ángulo ira de 360 a menos
            # si no queremos ver los ángulos, solo debemos poner draw = False (por defecto es True)
            angArmL = detector.findAngle(img, 13, 11, 23)
            # ahora haremos el brazo derecho (ángulo)
            angArmR = detector.findAngle(img, 14, 12, 24)

            # para hacer la postura de brazos cruzados necesitamos calcular
            # como en este caso las manos estarán pegadas a nuestros hombros
            # debemos calcular la distancia que hay de nuestras manos a nuestros hombros
            # iremos a los puntos y lo que tenemos que hacer es cuando la marca
            # 15 esté cerca de 12 y 16 esté cerca de 11 entonces reconocerá que los
            # brazos están cruzados, otra condición que podríamos añadir son los ángulos
            # esto se valorará más adelante
            distArmL, img, _ = detector.findDistance(15, 12, img)
            distArmR, img, _ = detector.findDistance(16, 11, img)

            # lo que hará es comprobar que el ángulo obtenido es semejante y aproximado a 90,
            # si es verdadero retorna TRUE, si es falso retorna FALSE
            # podemos definir un mínimo y un máximo por defecto este valor es 20
            # checkTposeL y checkTposeR servirán para comprobar el ángulo de la posición T
            checkTposeL = detector.angleCheck(angArmL, 90)
            checkTposeR = detector.angleCheck(angArmR, 270)
            # checkUpPoseL y checkUpPoseR servirán para comprobar el ángulo de ambos brazos levantados
            checkUpPoseL = detector.angleCheck(angArmL, 180)
            checkUpPoseR = detector.angleCheck(angArmR, 180)

            # Si el ángulo es correcto significa que la posición de T se está realizando
            if checkTposeL and checkTposeR:
                # se guarda el gesto para mostrarlo en pantalla
                gesture = 'Posicion T'
                # para la posición en T pararemos de que el dron nos deje de seguir
                trackingMode = False

            # Si el ángulo es correcto significa que la posición de brazos arriba se está realizando
            elif checkUpPoseL and checkUpPoseR:
                # se guarda el gesto para mostrarlo en pantalla
                # Tracking Mode
                gesture = 'Brazos arriba'

                # el dron comenzará a seguirnos
                trackingMode = True

            # primero comprobaremos que hay distancia y si la hay entrará la condición
            elif distArmL and distArmR:
                # para ello comprobaremos que si la posición de t es menor que 100 entonces
                # la reconozca como válida, si es válida significa que estamos cruzando los brazos
                if distArmL < 100 and distArmR < 100:
                    # se guarda el gesto para mostrarlo en pantalla
                    gesture = "Brazos cruzados"
                    # Por lo que si los brazos están cruzados y es correcto, procedemos a tomar una foto, por lo que
                    # el temporizador comenzará en 3 hacia 0 para tomar la foto
                    # es decir 3,2,1 selfi!
                    snapTimer = time.time()

            # si nuestro temporizador es mayor que 0 significa que alguna acción sucederá
            if snapTimer > 0:
                # lo que haremos será calcular tiempo actual menos timer para saber los segundos que transcurren
                totalTime = time.time()-snapTimer

                # no ponemos = porque hay veces que el temporizador pega saltos de milisegundos y puede
                # saltarse este número por lo que trabajaremos con mayor y menor
                # Si ha pasado entre 0 y 0.9 pondremos 3 (temporizador hacia atrás)
                if 0 < totalTime < 0.9:
                    # escribe en pantalla 3
                    cv2.putText(img, "3", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                # Si ha pasado entre 1 y 1.9 pondremos 2
                elif 1 < totalTime < 1.9:
                    # escribe en pantalla 2
                    cv2.putText(img, "2", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                # Si ha pasado entre 2 y 2.9 pondremos 1
                elif 2 < totalTime < 2.9:
                    # escribe en pantalla 1
                    cv2.putText(img, "1", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                # Una vez pasado los 3 segundos tomaremos la foto
                elif totalTime > 3:
                    # Guardamos la imagen en la carpeta saved
                    # La foto se guarda con el tiempo porque es la única forma de no sobreescribirse con el
                    # mismo nombre
                    cv2.imwrite(f'BodyGestureDetection/saved/{time.time()}.jpg', img)
                    # resetearemos el timer a 0 para que tras terminar la acción no este en un bucle continuo
                    snapTimer = 0
                    # escribe en pantalla "selfi!"
                    cv2.putText(img, "selfi!", (225, 260), cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 0), 5)
                    # esperamos 0.2 segundos
                    time.sleep(0.2)
            else:
                # Escribe en pantalla el gesto que se está realizando
                cv2.putText(img, gesture, (5, 40), cv2.FONT_HERSHEY_PLAIN, 2, colorGesture, 2)

            # en caso de que se active el modo seguimiento entrara este condicional
            if trackingMode:
                # envía movimientos al dron a realizar, le envía:
                # zval es Adelante y atrás (0, zval, 0, 0)
                # yval es arriba y abajo (0, 0, yval, 0)
                # xval es derecha e izquierda (0, 0, 0, xval)
                me.send_rc_control(0, -zVal, -yVal, xVal)
                # se muestra que el dron está siguiendo
                cv2.putText(img, "Siguiendo!", (460, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            else:
                # se para el seguimiento, por lo que el dron debe estar parado (0, 0, 0, 0)
                me.send_rc_control(0, 0, 0, 0)
                # se muestra que el dron no está siguiendo
                cv2.putText(img, "No siguiendo!", (400, 40), cv2.FONT_HERSHEY_PLAIN, 2, colorGesture, 2)

        # Se muestra la batería que tiene
        cv2.putText(img, str("Bateria: "), (0, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.putText(img, str(me.get_battery()), (140, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # Mostramos la imagen
        cv2.imshow("Image", img)
        # Esperamos
        cv2.waitKey(1)

        # Si se pulsa q el dron aterriza (es una tecla de emergencia)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            me.land()
            break

    # Si se pulsa q el dron aterriza (es una tecla de emergencia)
    cv2.destroyAllWindows()


# para ejecutar la función en main
if __name__ == '__main__':
    BodyGestureDetectionES()
