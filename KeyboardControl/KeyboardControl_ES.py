# Programa que sea capaz de controlar el teclado del pc para dar órdenes al dron
# Además capturar imágenes y guardarlas en el dispositivo de forma remota

# Importamos las siguientes librerías:
from djitellopy import tello
import KeyboardControl.KeyPressModule_ES as kpES
import time
import cv2

global image

def KeyboardControlES():

    # Inicializamos el módulo
    kpES.init()

    # para conectar a nuestro tello
    # creamos el objeto tello
    dron = tello.Tello()
    # conectamos con tello
    print("¿Estamos conectados?")
    # Nos debe devolver ok
    dron.connect()

    # Nos aseguramos que vaya correcto para ello imprimimos por pantalla la batería
    print("Estado de la batería: " + str(dron.get_battery()))

    # Inicializamos la camara
    dron.streamon()
    print("Camara inicializada")

    # Definimos una función que compruebe que la tecla es presionada
    def getKeyboardInput():
        # Left&Right (Izquierda y derecha) -> lr | Forward&Backward (Hacia delante y hacia atrás)-> fb
        # Up&Down (Arriba y abajo)-> ud | YourVelocity(Velocidad) -> yv
        lr, fb, ud, yv = 0, 0, 0, 0
        # Declaramos una variable para la velocidad
        speed = 50

        # Si clicamos en izquierda nos desplaza a la izquierda
        if kpES.getKeyES("LEFT"):
            lr = -speed
        # Si clicamos en derecha nos desplaza a la derecha
        elif kpES.getKeyES("RIGHT"):
            lr = speed

        # Si clicamos arriba nos desplaza hacia delante
        if kpES.getKeyES("UP"):
            fb = speed
        # Si clicamos abajo nos desplaza hacia detrás
        elif kpES.getKeyES("DOWN"):
            fb = -speed

        # W (sube), S (baja), A (gira izquierda(rotar)), D (gira derecha(rotar))
        if kpES.getKeyES("w"):
            ud = speed
        elif kpES.getKeyES("s"):
            ud = -speed

        if kpES.getKeyES("a"):
            yv = -speed
        elif kpES.getKeyES("d"):
            yv = speed

        # Q (aterriza) y "E" (despega)
        if kpES.getKeyES("q"):
            dron.land()
        if kpES.getKeyES("e"):
            dron.takeoff()

        # Tomar imagen con botón espacio y guardarla en el dispositivo actual
        if kpES.getKeyES("SPACE"):
            tiempo = time.time()
            cv2.imwrite(f"KeyboardControl/saved/{tiempo}.jpg", image)
            print(f"Foto tomada")
            time.sleep(0.1)

        return [lr, fb, ud, yv]

    # Hacemos un loop que este continuamente viendo si le enviamos una tecla
    while True:
        value = getKeyboardInput()
        dron.send_rc_control(value[0], value[1], value[2], value[3])

        # Mientras que sea verdadero obtendremos los frames del drone
        image = dron.get_frame_read().frame
        # Para procesar las imágenes más rapido
        image = cv2.resize(image, (640, 480))
        cv2.putText(image, str("Bateria: "), (0, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.putText(image, str(dron.get_battery()), (140, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        # creamos una ventana que nos muestra las imágenes
        cv2.imshow("Image", image)
        # le daremos un retraso para que la imagen no se quite automáticamente antes de verla (1 milisegundo)
        cv2.waitKey(1)

        time.sleep(0.05)


if __name__ == '__main__':
    KeyboardControlES()
