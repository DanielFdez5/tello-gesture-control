import FaceFollowing.FaceFollowingResult_ES
import FaceFollowing.FaceFollowingResult_EN
import KeyboardControl.KeyboardControl_ES
import KeyboardControl.KeyboardControl_EN
import Tested.FlyingDemo_ES
import Tested.FlyingDemo_EN
import Tested.ImageDemo_ES
import Tested.ImageDemo_EN
import Tested.TestedConnection_ES
import Tested.TestedConnection_EN
import HandGestures.HandGesturesResult_ES
import HandGestures.HandGesturesResult_EN
import BodyGestureDetection.BodyGestureDetectionResult_ES
import BodyGestureDetection.BodyGestureDetectionResult_EN

exitWhile = False
parar = False
option = 0
select = 0

def pedirNumeroEntero():

    correct = False
    num = 0
    while not correct:
        try:
            num = int(input("Seleccione una opción: // Choose an option: "))
            correct = True
        except ValueError:
            print("Error! Inténtalo de nuevo // Error! Try again")

    return num


while not exitWhile:
    print("Bienvenido al proyecto, seleccione un idioma a ejecutar! / Welcome to the project, choose a language!")
    print("1. Español / Spanish")
    print("2. Inglés / English")
    print("3. Salir / Exit")

    option = pedirNumeroEntero()

    if option == 1:
        print("Has seleccionado Español!")
        print("")
        print("")
        select = 1
        exitWhile = True
    elif option == 2:
        print("You have selected English!")
        print("")
        print("")
        select = 2
        exitWhile = True
    elif option == 3:
        print("Adiós! / Bye!")
        exit()
    else:
        print("Introduce una opción válida! / Introduce a valid option!")

salida = False
if select == 1:
    while not salida:
        print("¿Que funcionalidad desea ejecutar?")
        print("1. Probar la conexión con el dron")
        print("2. Probar el vuelo del dron")
        print("3. Probar la cámara del dron")
        print("4. Ejecutar la funcionalidad FaceFollowing")
        print("5. Ejecutar la funcionalidad BodyGestureDetection")
        print("6. Ejecutar la funcionalidad HandGestureDetection")
        print("7. Ejecutar la funcionalidad de Tomar Control desde PC")
        print("8. Salir")
        option = pedirNumeroEntero()

        if option == 1:
            print("Has seleccionado la prueba de conexión con el dron. Ejecutando...")
            print("¡Recuerda que si pulsas q en cualquier modo se parará de ejecutar!")
            Tested.TestedConnection_ES.TestedConnectionES()
        elif option == 2:
            print("Has seleccionado la prueba de volar el dron. Ejecutando...")
            print("¡Recuerda que si pulsas q en cualquier modo se parará de ejecutar!")
            Tested.FlyingDemo_ES.FlyingDemoES()
        elif option == 3:
            print("Has seleccionado la prueba de la cámara del dron. Ejecutando...")
            print("¡Recuerda que si pulsas q en cualquier modo se parará de ejecutar!")
            Tested.ImageDemo_ES.ImageDemoES()
        elif option == 4:
            print("Has seleccionado la ejecución de FaceFollowing. Ejecutando...")
            print("¡Recuerda que si pulsas q en cualquier modo se parará de ejecutar!")
            FaceFollowing.FaceFollowingResult_ES.FaceFollowingES()
        elif option == 5:
            print("Has seleccionado la ejecución de BodyGestureDetection. Ejecutando...")
            print("¡Recuerda que si pulsas q en cualquier modo se parará de ejecutar!")
            BodyGestureDetection.BodyGestureDetectionResult_ES.BodyGestureDetectionES()
        elif option == 6:
            print("Has seleccionado la ejecución de HandGestureDetection. Ejecutando...")
            print("¡Recuerda que si pulsas q en cualquier modo se parará de ejecutar!")
            HandGestures.HandGesturesResult_ES.HandGesturesES()
        elif option == 7:
            print("Has seleccionado la ejecución de Control Remoto desde PC. Ejecutando...")
            print("¡Recuerda que si pulsas q en cualquier modo se parará de ejecutar!")
            KeyboardControl.KeyboardControl_ES.KeyboardControlES()
        elif option == 8:
            print("Adiós!")
            exit()
        else:
            print("Introduce una opción válida! / Introduce a valid option")

elif select == 2:
    while not salida:
        print("What functionality do you want to run?")
        print("1. Test the connection with the drone")
        print("2. Test the drone flight")
        print("3. Test the camera of the drone")
        print("4. Execute FaceFollowing functionality")
        print("5. Execute BodyGestureDetection functionality")
        print("6. Execute HandGestureDetection functionality")
        print("7. Execute Take Control from PC functionality")
        print("8. Exit")

        option = pedirNumeroEntero()

        if option == 1:
            print("You have selected the connection test with the drone. Executing...")
            print("Remember that if you press q in any mode it will stop executing!")
            Tested.TestedConnection_EN.TestedConnectionEN()
        elif option == 2:
            print("You have selected the test to fly the drone. Executing....")
            print("Remember that if you press q in any mode it will stop executing!")
            Tested.FlyingDemo_EN.FlyingDemoEN()
        elif option == 3:
            print("You have selected the drone camera test. Executing...")
            print("Remember that if you press q in any mode it will stop executing!")
            Tested.ImageDemo_EN.ImageDemoEN()
        elif option == 4:
            print("You have selected to run FaceFollowing. Executing...")
            print("Remember that if you press q in any mode it will stop executing!")
            FaceFollowing.FaceFollowingResult_EN.FaceFollowingEN()
        elif option == 5:
            print("You have selected to run BodyGestureDetection. Executing...")
            print("Remember that if you press q in any mode it will stop executing!")
            BodyGestureDetection.BodyGestureDetectionResult_EN.BodyGestureDetectionEN()
        elif option == 6:
            print("You have selected to run HandGestureDetection. Running....")
            print("Remember that if you press q in any mode it will stop executing!")
            HandGestures.HandGesturesResult_EN.HandGesturesEN()
        elif option == 7:
            print("You have selected the Remote Control execution from PC. Executing...")
            print("Remember that if you press q in any mode it will stop executing!")
            KeyboardControl.KeyboardControl_EN.KeyboardControlEN()
        elif option == 8:
            print("Bye!")
            exit()
        else:
            print("Introduce una opción válida! / Introduce a valid option")
