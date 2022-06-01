import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
from cvzone.FaceDetectionModule import FaceDetector
from djitellopy import tello

#cap = cv2.VideoCapture(0)
# declaramos el objeto
# el máximo de manos es 1
detector = HandDetector(maxHands=1)
# detectamos la cara para medir la distancia al recuadro
detectorFace = FaceDetector()

# variable para guardar los gestios
gesture = ''

# importaremos los valores del dron
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamoff()
me.streamon()
me.takeoff()
me.move_up(80)

cv2.waitKey(1)

while True:
    img = me.get_frame_read().frame
    # nos aseguramos que la resolución de la imagen es la misma
    img = cv2.resize(img, (640, 480))
    #_, img = cap.read()

    # Detectar las manos de la imagen
    # por defecto dibujará automáticamente
    img = detector.findHands(img)

    # Para detectar los puntos y la bbox será
    # por defecto dibujará automáticamente
    lmList, bboxInfo = detector.findPosition(img)

    # para detectar la cara
    img, bboxs = detectorFace.findFaces(img)

    if bboxs:
        # ahora lo que haremos será guardar los parámetros de detección de la cara
        x, y, w, h = bboxs[0]["bbox"]

        # por consiguiente crearemos uan región de detección para detectar la mano y que así no detecte t0do el rato la
        # los movimientos de la mano sino en una zona concreta, en este caso cerca de la cara
        bboxRegion = x -175-50, y -75, 175, h+75

        # una vez definida la región la dibujaremos en este caso, será interactiva
        # cvzone.cornerRect(img, bboxRegion, rt=0, t=10, colorC=(0, 0, 255))

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
                # cvzone.cornerRect(img, bboxRegion, rt=0, t=10, colorC=(0, 255, 0))
                
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
                    # open hand
                    gesture = 'Stop doing!'
                elif nFingers == [0, 0, 0, 0, 0]:
                    # close hand
                    gesture = 'Stop dron!'
                    # lo que haremos será parar de hacer algún movimiento y aterrizar
                    me.land()
                elif nFingers == [0, 1, 0, 0, 0]:
                    # index
                    gesture = 'Go up!'
                    # lo que haremos será que el dron se mueva hacia arriba 20 cm
                    me.move_up(20)
                elif nFingers == [0, 1, 1, 0, ]:
                    gesture = 'Go down!'
                    # si abrimos la mano el dorn se mueve hacia abajo 20 cm
                    me.move_down(20)
                elif nFingers == [0, 1, 0, 0, 1]:
                    # Rock pose
                    gesture = 'Left flip!'
                    # lo que hará será realizar un flip a la izquierda
                    me.flip_left()
                elif nFingers == [1, 1, 0, 0, 1]:
                    # Spiderman
                    gesture = 'Right flip!'
                    # lo que hará será realizar un flip a la derecha
                    me.flip_right()
                elif nFingers == [1, 0, 0, 0, 0]:
                    gesture = 'Go right!'
                    # Thumb
                    me.move_right(20)
                elif nFingers == [0, 0, 0, 0, 1]:
                    # pinky
                    gesture = 'Go left!'
                    me.move_left(20)

                # decoracion de las palabras
                cv2.rectangle(img, (bboxRegion[0], bboxRegion[1] + bboxRegion[3] +10),
                              (bboxRegion[0] + bboxRegion[2], bboxRegion[1] + bboxRegion[3]+60),
                              (0, 255, 0), cv2.FILLED)

                # lo que haremos será mostrar por pantalla lo que esta reconociendo
                cv2.putText(img, f'{gesture}',
                            (bboxRegion[0]+10, bboxRegion[1] + bboxRegion[3] + 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        me.land()
        break

cv2.destroyAllWindows()

