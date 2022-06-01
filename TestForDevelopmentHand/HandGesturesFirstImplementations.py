import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
from cvzone.FaceDetectionModule import FaceDetector
import time

cap = cv2.VideoCapture(0)
# declaramos el objeto
# el máximo de manos es 1
detector = HandDetector(maxHands=1, detectionCon=0.8, minTrackCon=0.8)
contador = 0
# detectamos la cara para medir la distancia al recuadro
detectorFace = FaceDetector()

# Crearemos un temporizador para el selfie
snapTimer = 0
# crearemos un temporizador
timer = 0

# establecemos un color para cada gesto para que sea diferenciador
colorGesture = (0, 0, 255)

# variable para guardar los gestos
gesture = ''

# inicilizamos el temporizador
timer = time.time()
# seguimiento es falso
seguimiento = False

# PID para manejar el dron
hi, wi = 480, 640

xPID = cvzone.PID([0.22, 0, 0.1], wi // 2)
yPID = cvzone.PID([0.27, 0, 0.1], hi // 2, axis=1)
zPID = cvzone.PID([0.00016, 0, 0.00011], 150000, limit=[-20, 30])

while True:
    # Inicializamos los valores:
    xVal = 0
    yVal = 0
    zVal = 0

    _, img = cap.read()
    # Detectar las manos de la imagen
    # por defecto dibujará automáticamente
    img = detector.findHands(img)

    # Para detectar los puntos y la bbox será
    # por defecto dibujará automáticamente
    lmList, bboxInfo = detector.findPosition(img)

    # para detectar la cara
    imf, bboxs = detectorFace.findFaces(img, draw=True)

    if bboxs:
        # ahora lo que haremos será guardar los parámetros de detección de la cara
        x, y, w, h = bboxs[0]["bbox"]

        cx, cy = bboxs[0]['center']
        area = w * h

        xVal = int(xPID.update(cx))
        yVal = int(yPID.update(cy))
        zVal = int(zPID.update(area))
        print(zVal)

        # por consiguiente crearemos uan región de detección para detectar la mano y que así no detecte t0do el rato la
        # los movimientos de la mano sino en una zona concreta, en este caso cerca de la cara
        bboxRegion = x -175-50, y -75, 175, h+75

        # una vez definida la región la dibujaremos en este caso, será interactiva
        cvzone.cornerRect(img, bboxRegion, rt=0, t=10, colorC=(0, 0, 255))

        # ahora lo que haremos es si la mano derecha se encuentra en la región o no
        # si los dedos se detectan...
        # nos aseguramos que sea la mano derecha
        if lmList and detector.handType() == "Right":

            # por consiguiente encontraremos el centro
            handCenter = bboxInfo["center"]

            # una vez que tenemos el centro podremos chequear si esta en la region
            # inside es True or False y nos devolverá si está dentro o no
                        # x             center x            (x+w)
                        #y              center y            (y+h)
            inside = bboxRegion[0] < handCenter[0] < (bboxRegion[0]+bboxRegion[2]) and \
                     bboxRegion[1] < handCenter[1] < (bboxRegion[1] + bboxRegion[3])

            # si es inside es true, dibujaremos la region en verde simulando que esta dentro y es correcto
            if inside:
                cvzone.cornerRect(img, bboxRegion, rt=0, t=10, colorC=(0, 255, 0))
                
                # contaremos el número de dedos levantados
                nFingers = detector.fingersUp()

                # contaremos el número de dedos a través de la obtención de cada dedo
                # thumb, index, middle, ring, pinky = detector.fingersUp()
                # como vemos reducimos la complejidad y el número de parámetros
                if nFingers == [1, 1, 1, 1, 1]:
                    gesture = 'Stop!'
                    timer = time.time()
                    seguimiento = False

                elif nFingers == [0, 0, 0, 0, 0]:
                    gesture = 'Close hand'
                    timer = time.time()

                elif nFingers == [0, 1, 1, 0, 0]:
                    gesture = 'Selfi!'
                    # por lo que si los brazos están cruzados y es correcto, procedemos a tomar una foto, por lo que
                    # el temporizador comenzará en 3 hacia 0 para tomar la foto
                    snapTimer = time.time()
                    timer = time.time()

                elif nFingers == [0, 1, 1, 1, 0]:
                    seguimiento = True

                elif nFingers == [0, 1, 0, 0, 0]:
                    gesture = 'Index'

                elif nFingers == [0, 1, 0, 0, 1]:
                    gesture = 'Rock pose'

                # decoracion de las palabras
                cv2.rectangle(img, (bboxRegion[0], bboxRegion[1] + bboxRegion[3] +10),
                              (bboxRegion[0] + bboxRegion[2], bboxRegion[1] + bboxRegion[3]+60),
                              (0,255,0), cv2.FILLED)

                # lo que haremos será mostrar por pantalla lo que esta reconociendo
                cv2.putText(img, f'{gesture}',
                            (bboxRegion[0]+10, bboxRegion[1] + bboxRegion[3] + 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)


        # si nuestro temporizador es mayor que 0 significa que alguna acción sucederá
        if snapTimer > 0:
                # lo que haremos será calcular tiempo actual menos timer para saber los segundos que transcurren
                totalTime = time.time() - snapTimer
                print(totalTime)

                # no ponemos = porque hay veces que el temporizador pega saltos de milisegundos y puede saltarse este número
                if 0 < totalTime < 0.9:
                    cv2.putText(img, "3", (650, 400), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                elif 1 < totalTime < 1.9:
                    cv2.putText(img, "2", (650, 400), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                elif 2 < totalTime < 2.9:
                    cv2.putText(img, "1", (650, 400), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)

                elif totalTime > 3:
                    # guardamos la imagen
                    cv2.imwrite(f'saved/{time.time()}.jpg', img)

                    # resetearemos el timer a 0 para que tras terminar la acción no este en un bucle continuo
                    snapTimer = 0
                    cv2.putText(img, "selfie!", (650, 400), cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 0), 5)
                    time.sleep(0.2)
        else:
            cv2.putText(img, gesture, (5, 40), cv2.FONT_HERSHEY_PLAIN, 2, colorGesture, 2)

        # si nuestro temporizador es mayor que 0 significa que alguna acción sucederá
        if timer > 0:
            # lo que haremos será calcular tiempo actual menos timer para saber los segundos que transcurren
            totalTime = time.time() - timer
            print(totalTime)

            if totalTime > 5:
                # resetearemos el timer a 0 para que tras terminar la acción no este en un bucle continuo
                timer = 0
                print("Listo")
                time.sleep(0.2)
                # Ponemos el seguimiento en true
                seguimiento = True

        if seguimiento:
            # me.send_rc_control(0, -zVal, -yVal, xVal)
            print("siguiendo")
            cv2.putText(img, "Seguimiento: ", (850, 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
            cv2.putText(img, "Activado", (1080, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        else:
            # me.send_rc_control(0, 0, 0, 0)
            print("no siguiendo")
            cv2.putText(img, "Seguimiento: ", (850, 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
            cv2.putText(img, "No activado", (1080, 40), cv2.FONT_HERSHEY_PLAIN, 2, colorGesture, 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
