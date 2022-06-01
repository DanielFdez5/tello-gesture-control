# We import pygame for the driver
import pygame

# create a "game" window
# New function that will initialize pygame
def init():
    pygame.init()
    win = pygame.display.set_mode((400, 400))

# We will get the key pressed
def getKeyEN(keyName):
    # If the key is pressed it returns true and otherwise false.
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
    if getKeyEN("LEFT"):
        print("LEFT KEY PRESSED")
    if getKeyEN("RIGHT"):
        print("RIGHT KEY PRESSED.")


# If I run this as the main file then do this
if __name__ == '__main__':
    init()

