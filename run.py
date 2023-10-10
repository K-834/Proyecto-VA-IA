import backendFace as faceVAIA

# EJECUCION DEL PROYECTO

if __name__ == "__main__":

    metodo = input("Ingresa el número del método que deseas utilizar: ")

    if metodo == "1":
        tipoVideo = 0
    elif metodo == "2":
        tipoVideo = "prueba/ejemplo2.mp4"
    elif metodo == "3":
        ip_address = "192.123.231.1"
        port = 8080
        tipoVideo = f"http://{ip_address}:{port}/video"
    else:
        print("Método no válido. Por favor, selecciona una opción válida.")

    if tipoVideo:

        faceVAIA.opencv_processing(tipoVideo)   #modelo enfocado al envio de imagenes y texto WHATSAPP
        faceVAIA.VerificacionSesion()           #verificación de datos biometricos
        faceVAIA.run3(tipoVideo)                #verificación de rostros
