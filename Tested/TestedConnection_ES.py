from djitellopy import tello
import cv2

def TestedConnectionES():
    # objetos para importar tello
    me = tello.Tello()
    # conectamos nuestro tello
    me.connect()
    print("Conectado!")
    print("Batería: ")
    # Nivel de batería
    print(me.get_battery())
    # esperamos
    cv2.waitKey(5000)
    print("Prueba hecha!")
    # esperamos
    cv2.waitKey(2000)
    print("Vas a ser desconectado...")
    # esperamos
    cv2.waitKey(2000)
    print("")
    print("")
    print("")

if __name__ == '__main__':
    TestedConnectionES()
