from cvzone.PoseModule import PoseDetector
import cv2
from djitellopy import tello

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamoff()
me.streamon()

detector = PoseDetector(upBody=True)
#cap = cv2.VideoCapture(0)

while True:
    _, img = cap.read()

    # ahora lo que debemos hacer es conseguir los puntos a través de:
    # aqui tambén podemos borrar el dibujo poniendo draw = False
    img = detector.findPose(img, draw=False)
    # guardaremos la información de los puntos en lmlist (landmarks) y de la bbox en bboxInfo
    lmList, bboxInfo = detector.findPosition(img)

    # guardaremos aquí los movimientos
    gesture = ''

    # lo primero que haremos será buscar el ángulo
    # primero imprimiremos los valores para verlo
    # print(lmList)

    # para los puntos que tenemos que ver y calcular su angulo para la t-pose y up pose serán
    # 12-14-24 y 11-13-23
    # si este ángulo está alrededor de los 90 grados o un poco mas o menos tendremos la posición t
    # en cambio si los ángulos esten sobre los 180 grados entonces hablaremos que los brazos están en alto
    # para hacer esto:

    # añadimos una condición para evitar un error si no hay imagen no proceses el ángulo
    if bboxInfo:

        # primero haremos el brazo izquierdo (ángulo)
        # hay que asegurarse que el punto del medio sea el p2, los extremos son indiferentes
        # si ponemos los puntos al revés lo que pasará es que el angulo ira de 360 a menos
        # sino queremos ver los ángulos, solo debemos poner draw = False, sino ponemos nada,
        # por defecto es True
        angArmL = detector.findAngle(img, 13, 11, 23, draw=False)

        # ahora haremos el brazo derecho (ángulo)
        angArmR = detector.findAngle(img, 14, 12, 24, draw=False)

        # para hacer la postura de brazos cruzados necesitamos calcular
        # como en este caso las manos estarán pegadas a nuestros hombros
        # debemos calcular la distancia a de nuestras manos a nuestros hombros
        # iremos a los puntos y lo que tenemos que hacer es cuando la marca
        # 15 esté cerca de 12 y 16 esté cerca de 11 entonces reconocerá que los
        # brazos están cruzados, otra condición que podríamos añadir son los ángulos
        # esto se valorará más adelante
        distArmL, img, _ = detector.findDistance(15, 12, img)
        distArmR, img, _ = detector.findDistance(16, 11, img)

        # lo que hará es comprobar que el ángulo obtenido es semajnte y aproximado a 90, si es verdadero retorna TRUE
        # si es falso retorna FALSE
        # podemos definir un mínimo y un máximo por defecto es 20
        checkTposeL = detector.angleCheck(angArmL, 90)
        checkTposeR = detector.angleCheck(angArmR, 270)

        checkUpPoseL = detector.angleCheck(angArmL, 180)
        checkUpPoseR = detector.angleCheck(angArmR, 180)

        if checkTposeL and checkTposeR:
            gesture = 'Posicion T!'

        elif checkUpPoseL and checkUpPoseR:
            gesture = 'Manos Arriba!'

        # primero comprobaremos que hay distancia y si la hay
        elif distArmL and distArmR:
            # para ello comprobaremos que si la posiciónde t es menor que 100 entonces la reconozca como valida
            if distArmL < 100 and distArmR < 100:
                gesture = "Brazos cruzados"

        cv2.putText(img, gesture, (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
