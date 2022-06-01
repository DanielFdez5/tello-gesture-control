from djitellopy import tello
import cv2

def ImageDemoES():
    # creamos el objeto
    me = tello.Tello()
    # conectamos el dron
    me.connect()
    # imprimimos el porcentaje de batería
    print(me.get_battery())

    # apagamos la cámara
    me.streamoff()
    # encendemos la cámara
    me.streamon()

# mientras sea verdadero...
    while True:
        # esto nos da la imagen de la cámara del dron
        img = me.get_frame_read().frame
        # la reajusta a 640x480
        img = cv2.resize(img, (640, 480))
        # la mostramos con el nombre de Image
        cv2.imshow("Image", img)

        # si presionas el botón q se apagará
        if cv2.waitKey(5) & 0xFF == ord('q'):  # 5 miliseconds
            me.streamoff()
            break

        print("Camara funcionando!")
        # esperamos
        cv2.waitKey(5000)
        print("Prueba hecha!")
        # esperamos
        cv2.waitKey(2000)
        print("Vas a ser desconectado...")
        # esperamos
        cv2.waitKey(2000)
        # desconectamos
        me.streamoff()
        # destruimos la ventana que se ha abierto con la imagen
        cv2.destroyAllWindows()
        break

    # desconectamos...
    print("Desconectando...")
    print("")
    print("")


if __name__ == '__main__':
    ImageDemoES()
