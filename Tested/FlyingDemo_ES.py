from djitellopy import tello
import time
import cv2

def FlyingDemoES():

    # objetos para importar tello
    me = tello.Tello()
    # conectamos nuestro tello
    me.connect()
    # obtenemos el porcentaje de batería
    print(me.get_battery())

    # el dron inicia
    me.takeoff()

    # subir drone un poco mas que por defecto
    # Tambien podría escribirse como me.move('up',80)
    # moverse con distancia
    me.move_up(80) # 80 cm

    # para mover el dron no se le dice ve y muevete 50 cm
    # si no se cambia su velocidad hasta llegar a ese punto
    # rango desde -100 hasta 100
    # 1 -> left_right
    # 2 -> forward, backward
    # 3 -> up, down
    # 4 -> yaw
    # moverse con velocidad

    # Probando izquierda
    print("Probando izquierda")
    me.send_rc_control(-20, 0, 0, 0)
    print("Test hecho")
    time.sleep(1) # 1 segundos

    # Probando derecha
    print("Probando derecha")
    me.send_rc_control(20, 0, 0, 0)
    print("Test hecho")
    time.sleep(1) # 1 segundos

    # Probando hacia delante
    print("Probando hacia delante")
    me.send_rc_control(0, 20, 0, 0)
    print("Test hecho")
    time.sleep(1) # 1 segundos

    # Probando hacia atrás
    print("Probando hacia atrás")
    me.send_rc_control(0, -20, 0, 0)
    print("Test hecho")
    time.sleep(1) # 1 segundos

    # Probando arriba
    print("Probando arriba")
    me.send_rc_control(0, 0, 20, 0)
    print("Test hecho")
    time.sleep(1) # 1 segundos

    # Probando abajo
    print("Probando abajo")
    me.send_rc_control(0, 0, -20, 0)
    print("Test hecho")
    time.sleep(1) # 1 segundos

    # Probando rotación izquierda
    print("Probando rotación izquierda")
    me.send_rc_control(0, 0, 0, -90)
    print("Test hecho")
    time.sleep(1) # 1 segundos

    # Probando rotación derecha
    print("Probando rotación derecha")
    me.send_rc_control(0, 0, 0, 90)
    print("Test hecho")
    time.sleep(1) # 1 segundos

    # Ahora daremos una velocidad en un tiempo
    time.sleep(1) # 1 segundos

    # Aseguramos que el dron este parado
    me.send_rc_control(0, 0, 0, 0)

    # Lo aterrizamos
    me.land()

    # Esperamos
    cv2.waitKey(5000)
    print("Prueba hecha!")
    # Esperamos
    cv2.waitKey(2000)
    print("Vas a ser desconectado...")
    cv2.waitKey(2000)
    print("")
    print("")
    print("")


if __name__ == '__main__':
    FlyingDemoES()
