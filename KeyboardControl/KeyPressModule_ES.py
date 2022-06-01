# Importamos pygame para el controlador
import pygame

# creamos una ventana de "juego"
# Nueva función que inicializará pygame
def init():
    pygame.init()
    win = pygame.display.set_mode((400, 400))

# Obtendremos la tecla pulsada
def getKeyES(keyName):
    # Si la tecla es pulsada devuelve true y sino false
    ans = False

    for eve in pygame.event.get():
        pass
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput [myKey]:
        ans = True
    pygame.display.update()
    return ans

def main():
    if getKeyES("LEFT"):
        print("TECLA IZQUIERDA PRESIONADA")
    if getKeyES("RIGHT"):
        print("TECLA DERECHA PRESIONADA")


# Si ejecuto esto como el archivo principal entonces haz esto
if __name__ == '__main__':
    init()
