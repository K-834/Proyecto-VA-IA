import backendFace as faceVAIA

# EJECUCION DEL PROYECTO

if __name__ == "__main__":
    # video = "prueba/ejemplo2.mp4"

    Tvideo = input("Metodo de video : ")

    if Tvideo == "0":
        tipoVideo = 0

    if Tvideo == "1":
        tipoVideo = "prueba/ejemplo2.mp4"

    if Tvideo == "2":
        ip_address = "192.168.0.100"  # Reemplaza con la IP de tu teléfono
        port = 8080  # Reemplaza con el puerto configurado en la aplicación
        tipoVideo = f"http://{ip_address}:{port}/video"


    # faceVAIA.opencv_processing(tipoVideo)   #modelo enfocado al envio de imagenes y texto WHATSAPP
    # faceVAIA.VerificacionSesion()           #verificación de datos biometricos
    # faceVAIA.run3(tipoVideo)                #verificación de rostros
