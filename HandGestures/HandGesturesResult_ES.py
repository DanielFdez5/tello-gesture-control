# Importamos las librerías
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
from cvzone.FaceDetectionModule import FaceDetector
import time
from djitellopy import tello

# Función que ejecutará la funcionalidad en el main.py
def HandGesturesES():
    # Detectar la mano mediante el objeto HandDetector
    # maxHands: número máximo de manos (por defecto 2)
    # detectionCon (0 - 1): Precisión de detección
    # trackCon (0 - 1): seguimientos puntos de referencia
    detector = HandDetector(maxHands=1, detectionCon=0.75, minTrackCon=0.75)

    # Detectar la cara mediante el objeto FaceDetector
    # objeto detector (Por defecto valor mínimo 0.5) si queremos que sea más preciso debemos subir este a 0.7 o más
    detectorFace = FaceDetector(minDetectionCon=0.75)

    # Crearemos un temporizador para el selfie
    snapTimer = 0

    # Establecemos un color para los gestos
    colorGesture = (0, 0, 255)

    # Variable para guardar los gestos
    gesture = ''

    # Inicializamos el temporizador
    timer = time.time()

    # Inicializamos la variable que identificará si nos está siguiendo o no (por defecto False)
    seguimiento = False

    # Márgenes del video
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
    zPID = cvzone.PID([0.005, 0, 0.003], 12000, limit=[-20, 30])

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

    # Esperamos 1 segundo
    cv2.waitKey(1)

    # Bucle mientras que sea verdadera la obtención de imágenes
    while True:

        # Obtenemos la imagen
        img = me.get_frame_read().frame
        # Resize para que vaya más fluido
        img = cv2.resize(img, (640, 480))

        # Ahora lo que debemos hacer es conseguir los puntos a través de findHands(podemos borrar
        # el dibujo poniendo draw = False)
        img = detector.findHands(img)
        # Guardaremos la información de los puntos en lmlist (landmarks) y de la bbox en bboxInfo
        lmList, bboxInfo = detector.findPosition(img)

        # Ahora lo que debemos hacer es conseguir la cara mediante findFaces (podemos borrar
        # el dibujo poniendo draw = False)
        imf, bboxs = detectorFace.findFaces(img, draw=True)

        # Inicializamos los valores:
        # Dichos valores envían la distancia que tiene que recorrer el dron para reposicionarse de manera correcta
        xVal = 0
        yVal = 0
        zVal = 0

        # Añadimos una condición para evitar un error si no hay imagen
        if bboxs:

            # De la bonding box tomamos x y ancho y largo
            x, y, w, h = bboxs[0]["bbox"]
            # Tomamos valores de la bbox como son: centro de x y de y
            cx, cy = bboxs[0]['center']
            # el área será igual al largo por el ancho de la bbox que rodee a nuestro cara
            area = w * h

            # para controlar que el dron se mantenga siempre en el centro de la imagen, lo que haremos será usar
            # un PID controller, para que la imagen esté estabilizada
            xVal = int(xPID.update(cx))
            yVal = int(yPID.update(cy))
            zVal = int(zPID.update(area))

            # por consiguiente crearemos uan región de detección para detectar la mano y
            # que así no detecte constantemente los movimientos de la mano, sino en una zona concreta,
            # en este caso cerca de la cara
            bboxRegion = x -175-50, y -75, 175, h+75

            # una vez definida la región la dibujaremos en este caso, será interactiva
            # si no hay mano aparecerá en color rojo y si la hay aparecerá en color verde
            cvzone.cornerRect(img, bboxRegion, rt=0, t=10, colorC=(0, 0, 255))

            # Ahora lo que haremos es detectar si la mano derecha se encuentra en la región o no
            # y si de este, está detectando los dedos
            # Hay que asegurarse que la mano sea derecha ("Right")
            if lmList and detector.handType() == "Right":

                # Por consiguiente lo que haremos será encontrar el centro
                handCenter = bboxInfo["center"]

                # una vez que tenemos el centro podremos chequear si esta en la region
                # inside es True or False y nos devolverá si está dentro o no
                            # x             center x            (x+w)
                            # y              center y            (y+h)
                inside = bboxRegion[0] < handCenter[0] < (bboxRegion[0]+bboxRegion[2]) and \
                         bboxRegion[1] < handCenter[1] < (bboxRegion[1] + bboxRegion[3])

                # si inside es true, dibujaremos la region en verde simulando que está dentro y es correcto
                if inside:
                    # Dibujamos la zona en verde
                    cvzone.cornerRect(img, bboxRegion, rt=0, t=10, colorC=(0, 255, 0))

                    # Contaremos el número de dedos levantados para poder interpretar los movimientos,
                    # ya que los dedos los cuenta de la siguiente forma:
                    # levantado: 1
                    # no levantado: 0
                    nFingers = detector.fingersUp()

                    # Contaremos el número de dedos a través de la obtención de cada dedo
                    # thumb, index, middle, ring, pinky = detector.fingersUp()
                    # como vemos reducimos la complejidad y el número de parámetros

                    # Si la palma está levantada entonces:
                    # Gesto = "Parar!", el timer vuelve a 0 y deja de seguir al usuario
                    if nFingers == [1, 1, 1, 1, 1]:

                        # Guardamos el gesto Parar!
                        gesture = 'Parar!'
                        # Reiniciamos contador
                        timer = time.time()
                        # Establecemos el seguimiento en False
                        seguimiento = False

                    # Si el pulgar, índice y meñique están levantados
                    # Gesto = "Selfi!", el timer vuelve a 0, se inicializa el timer de selfi y deja de seguir
                    # al usuario
                    elif nFingers == [1, 1, 0, 0, 1]:

                        # Guardamos el gesto Selfi!
                        gesture = 'Selfi!'
                        # procedemos a tomar una foto, por lo que el temporizador comenzará en 3 hacia 0
                        # para tomar la foto
                        snapTimer = time.time()
                        # Reiniciamos el contador
                        timer = time.time()
                        # Establecemos el seguimiento en False
                        seguimiento = False

                    # Si el índice, corazón y anular están levantados
                    # Gesto = "Seguir!", se inicializa el seguimiento
                    elif nFingers == [0, 1, 1, 1, 0]:
                        # Guardamos el gesto Seguir!
                        gesture = 'Seguir!'
                        # Establecemos el seguimiento en True
                        seguimiento = True

                    # Si el índice está levantado
                    # Gesto = "Arriba!", el dron se desplaza hacia arriba, el timer vuelve a 0
                    # y deja de seguir
                    elif nFingers == [0, 1, 0, 0, 0]:
                        # Guardamos el gesto Arriba!
                        gesture = 'Arriba!'
                        # El dron se desplaza 20 hacia arriba
                        me.send_rc_control(0, 0, 20, 0)
                        # Reiniciamos el contador
                        timer = time.time()
                        # Establecemos el seguimiento en False
                        seguimiento = False

                    # Si el pulgar está levantado
                    # Gesto = "Abajo!", el dron se desplaza hacia abajo, el timer vuelve a 0
                    # y deja de seguir
                    elif nFingers == [1, 0, 0, 0, 0]:
                        # Guardamos el gesto Abajo!
                        gesture = 'Abajo!'
                        # El dron se desplaza 20 hacia abajo
                        me.send_rc_control(0, 0, -20, 0)
                        # Reiniciamos el contador
                        timer = time.time()
                        # Establecemos el seguimiento en False
                        seguimiento = False

                    # Si el índice y corazón están levantados
                    # Gesto = "Derecha!", el dron se desplaza a la derecha, el timer vuelve a 0
                    # y deja de seguir
                    elif nFingers == [0, 1, 1, 0, 0]:
                        # Guardamos el gesto Derecha!
                        gesture = 'Derecha!'
                        # El dron se desplaza 20 a la derecha
                        me.send_rc_control(20, 0, 0, 0)
                        # Reiniciamos el contador
                        timer = time.time()
                        # Establecemos el seguimiento en False
                        seguimiento = False

                    # Si el pulgar y meñique están levantados
                    # Gesto = "Abajo!", el dron se desplaza hacia abajo, el timer vuelve a 0
                    # y deja de seguir
                    elif nFingers == [1, 0, 0, 0, 1]:
                        # Guardamos el gesto Izquierda!
                        gesture = 'Izquierda!'
                        # El dron se desplaza 20 a la izquierda
                        me.send_rc_control(-20, 0, 0, 0)
                        # Reiniciamos el contador
                        timer = time.time()
                        # Establecemos el seguimiento en False
                        seguimiento = False

                    # Se decoran las palabras que muestra en la región, justo debajo de esta en un color verde
                    cv2.rectangle(img, (bboxRegion[0], bboxRegion[1] + bboxRegion[3] +10),
                                  (bboxRegion[0] + bboxRegion[2], bboxRegion[1] + bboxRegion[3]+60),
                                  (0,255,0), cv2.FILLED)

                    # Lo que haremos será mostrar por pantalla lo que está reconociendo en ese momento
                    cv2.putText(img, f'{gesture}',
                                (bboxRegion[0]+10, bboxRegion[1] + bboxRegion[3] + 50),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

            # Si nuestro temporizador es mayor que 0 significa que alguna acción sucederá
            # en este caso la acción asociada es tomar una foto
            if snapTimer > 0:

                # Lo que haremos será calcular tiempo actual menos timer para saber los segundos
                # que transcurren
                totalTime = time.time() - snapTimer

                # no ponemos = porque hay veces que el temporizador pega saltos de milisegundos y puede
                # saltarse este número por lo que trabajaremos con mayor y menor
                # Si ha pasado entre 0 y 0.9 pondremos 3 (temporizador hacia atrás)
                if 0 < totalTime < 0.9:
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
                    cv2.imwrite(f'HandGestures/saved/{time.time()}.jpg', img)

                    # resetearemos el timer a 0 para que tras terminar la acción no este en un bucle continuo
                    snapTimer = 0
                    # escribe en pantalla "selfi!"
                    cv2.putText(img, "selfi!", (650, 400), cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 0), 5)
                    # esperamos 0.2 segundos
                    time.sleep(0.2)
            else:
                # Escribe en pantalla el gesto que se está realizando
                cv2.putText(img, gesture, (5, 40), cv2.FONT_HERSHEY_PLAIN, 2, colorGesture, 2)

            # Si nuestro temporizador es mayor que 0 significa que alguna acción sucederá
            # en este caso la acción asociada es comenzar el seguimiento tras estar 7 segundos
            # si en 7 segundos no ha habido acción comienza el seguimiento automaticamente
            if timer > 0:
                # lo que haremos será calcular tiempo actual menos timer para saber los segundos que transcurren
                totalTime = time.time() - timer
                # Una vez han pasado 7 segundos, comienza el seguimiento
                if totalTime > 7:
                    # resetearemos el timer a 0 para que tras terminar la acción no este en un bucle continuo
                    timer = 0
                    # esperamos 0.2 segundos
                    time.sleep(0.2)
                    # Ponemos el seguimiento en True
                    seguimiento = True

            # Se muestra la batería que tiene
            cv2.putText(img, str("Bateria: "), (0, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            cv2.putText(img, str(me.get_battery()), (140, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            # Si seguimiento es verdadero el dron comienza a seguirte
            if seguimiento:
                # envía movimientos al dron a realizar, le envía:
                # zval es Adelante y atrás (0, zval, 0, 0)
                # yval es arriba y abajo (0, 0, yval, 0)
                # xval es derecha e izquierda (0, 0, 0, xval)
                me.send_rc_control(0, -zVal, -yVal, xVal)
                # se muestra que el dron está siguiendo
                cv2.putText(img, "Siguiendo!", (460, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            # Si seguimiento es falso el dron para de seguirte
            else:
                # se para el seguimiento, por lo que el dron debe estar parado (0, 0, 0, 0)
                me.send_rc_control(0, 0, 0, 0)
                # se muestra que el dron no está siguiendo
                cv2.putText(img, "No siguiendo!", (400, 40), cv2.FONT_HERSHEY_PLAIN, 2, colorGesture, 2)

        # Mostramos la imagen
        cv2.imshow("Image", img)
        # Esperamos
        cv2.waitKey(1)


# Para ejecutar la función en main.py
if __name__ == '__main__':
    HandGesturesES()
