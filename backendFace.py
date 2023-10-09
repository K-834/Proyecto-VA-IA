import deepface.DeepFace
import numpy as np
import cv2
from ultralytics import YOLO
from sort import Sort
import datetime
import os
from deepface import DeepFace
import pywhatkit as kit
import time

confi = 0.5
clase = [0]

database_dir = [
        "C:\\Users\\antho\\OneDrive\\Documentos\\GitHub\\Proyecto-VA-IA\\database\\Juanita\\Juanita1.png"
    ]
verification_cache = {}
tracker_cache = {}
unknown_person_detected = False
unknown_persons_dir = "Personas_Desconocidas"
if not os.path.exists(unknown_persons_dir):
    os.makedirs(unknown_persons_dir)

def send_whatsapp_message(phone_number, message, image_paths):
    # kit.sendwhats_image(phone_number, audio_path)
    time.sleep(4)
    # Envía las imágenes de personas desconocidas
    for image_path in image_paths:
        kit.sendwhats_image(phone_number, image_path, tab_close=True)
        time.sleep(1)  # Espera un tiempo entre el envío de cada imagen

    # Envía el mensaje de WhatsApp después de enviar las imágenes
    kit.sendwhatmsg_instantly(phone_number, message,tab_close=True)
    pass

# Función para realizar la verificación de personas desconocidas que han sido rastreadas durante un tiempo especificado
def check_unknown_person_tracking(tracker_cache, max_tracking_time):
    unknown_person_detected = False
    for track_id, track_info in list(tracker_cache.items()):
        if track_info["tracking_time"] >= max_tracking_time:
            unknown_person_detected = True
            break
    return unknown_person_detected

# modelo identificación de objetos [personas]
def run1(tipoVideo):
    cap = cv2.VideoCapture(tipoVideo)

    model = YOLO("yolov8n.pt")

    paused = False

    while cap.isOpened():

        if not paused:
            status, frame = cap.read()

            if not status:
                break

            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            results = model.predict(source=frame, save=True, classes=clase, conf=confi)

            frame = results[0].plot()

            cv2.putText(frame, formatted_datetime, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("CAMARA VIGILANCIA", frame)

            for i, result in enumerate(results):
                # Guarda cada imagen detectada en la carpeta "runs/detect"
                image_name = f"detected_{i}.jpg"  # Nombre de archivo para la imagen detectada
                image_path = os.path.join("runs", "deteccion", image_name)
                cv2.imwrite(image_path, result.plot())

        key = cv2.waitKey(1)

        if key == 27:
            break
        elif key == 32:
            paused = not paused

    print("Eso es todo")
    cap.release()
    cv2.destroyAllWindows()

# modelo verificación de personas por rostros
def run2(tipoVideo):
    cap = cv2.VideoCapture(tipoVideo)

    model = YOLO("yolov8n.pt")

    tracker = Sort()

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    while cap.isOpened():
        status, frame = cap.read()

        if not status:
            break

        results = model(frame, stream=True,classes=clase)

        for res in results:
            filtered_indices = np.where(res.boxes.conf.cpu().numpy() > confi)[0]
            boxes = res.boxes.xyxy.cpu().numpy()[filtered_indices].astype(int)
            tracks = tracker.update(boxes)
            tracks = tracks.astype(int)

            for xmin, ymin, xmax, ymax, track_id in tracks:
                cv2.putText(img=frame, text="Desconocido", org=(xmin, ymin - 10), fontFace=cv2.FONT_HERSHEY_PLAIN,
                            fontScale=1.0, color=(0, 0, 255), thickness=2)

                cv2.rectangle(img=frame, pt1=(xmin, ymin), pt2=(xmax, ymax), color=(0, 0, 255), thickness=2)

            # frame = results[0].plot()




        cv2.putText(frame, formatted_datetime, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("CAMARA VIGILANCIA", frame)


        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()


# modelo tracking de desconocidos y envio de mensajes
def run3(tipoVideo):
    cap = cv2.VideoCapture(tipoVideo)

    # Inicializa el modelo YOLOv8n de Ultralytics
    model = YOLO("yolov8n.pt")

    # Inicializa el tracker de personas (Sort)
    tracker = Sort()

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Directorio de la base de datos de caras conocidas

    while cap.isOpened():
        status, frame = cap.read()

        if not status:
            break

        # Realizar la detección de objetos con YOLOv8n
        results = model(frame, stream=True, classes=clase)

        for res in results:
            filtered_indices = np.where(res.boxes.conf.cpu().numpy() > confi)[0]
            boxes = res.boxes.xyxy.cpu().numpy()[filtered_indices].astype(int)
            tracks = tracker.update(boxes)
            tracks = tracks.astype(int)

            for xmin, ymin, xmax, ymax, track_id in tracks:
                # Extraer la región de interés (ROI) de la persona detectada
                roi = frame[ymin:ymax, xmin:xmax]

                # Crear un archivo temporal para la ROI
                roi_path = "temp_roi.png"
                cv2.imwrite(roi_path, roi)

                # Verificar si el archivo temporal existe
                if os.path.exists(roi_path):
                    # Comprueba si el track_id ya está en la caché de verificación
                    if track_id in verification_cache:
                        verification_results = verification_cache[track_id]
                    else:
                        # Inicializar una lista para almacenar los resultados de verificación
                        verification_results = []

                        # Iterar a través de la base de datos de caras conocidas
                        for db_image_path in database_dir:
                            # Realizar la verificación facial con DeepFace para cada imagen en la base de datos
                            # Usar los archivos temporales creados
                            verification_result = DeepFace.verify(img1_path=roi_path, img2_path=db_image_path,enforce_detection=False)
                            verification_results.append(verification_result)

                        # Almacenar el resultado en la caché de verificación
                        verification_cache[track_id] = verification_results

                    # Eliminar el archivo temporal de la ROI
                    os.remove(roi_path)

                    # Comprobar si la persona es conocida o desconocida
                    min_distance = min(result['distance'] for result in verification_results)

                    # Definir un umbral de compatibilidad
                    umbral_de_compatibilidad = 0.5  # Puedes ajustar este valor según tus necesidades

                    # Dibujar la etiqueta en el cuadro junto con el nombre de la imagen de la base de datos
                    filename = os.path.basename(db_image_path)
                    # Comprobar si la persona es conocida o desconocida
                    if min_distance <= umbral_de_compatibilidad:
                        label = f"Conocido ({filename})({track_id})"
                        color = (0, 255, 0)
                    else:
                        label = f"Desconocido ({track_id})"
                        color = (0, 0, 255)

                    cv2.putText(img=frame, text=label, org=(xmin, ymin - 10),
                                fontFace=cv2.FONT_HERSHEY_PLAIN,
                                fontScale=1.0, color=color, thickness=2)

                    cv2.rectangle(img=frame, pt1=(xmin, ymin), pt2=(xmax, ymax), color=color, thickness=2)

        cv2.putText(frame, formatted_datetime, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("CAMARA VIGILANCIA", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


# Función para enviar un mensaje por WhatsApp

# Función para el procesamiento de OpenCV en segundo plano
def opencv_processing(tipoVideo):
    global unknown_person_detected

    cap = cv2.VideoCapture(tipoVideo)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 30)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 30)

    # Inicializa el modelo YOLOv8n de Ultralytics
    model = YOLO("yolov8n.pt")

    # Inicializa el tracker de personas (Sort)
    tracker = Sort()

    while cap.isOpened():
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        status, frame = cap.read()

        if not status:
            break

        # Realizar la detección de objetos con YOLOv8n
        results = model(frame, stream=True, classes=clase)

        for res in results:
            filtered_indices = np.where(res.boxes.conf.cpu().numpy() > confi)[0]
            boxes = res.boxes.xyxy.cpu().numpy()[filtered_indices].astype(int)
            tracks = tracker.update(boxes)
            tracks = tracks.astype(int)

            for xmin, ymin, xmax, ymax, track_id in tracks:
                # Extraer la región de interés (ROI) de la persona detectada
                roi = frame[ymin:ymax, xmin:xmax]

                # Crear un archivo temporal para la ROI
                roi_path = "temp_roi.png"
                cv2.imwrite(roi_path, roi)

                # Verificar si el archivo temporal existe
                if os.path.exists(roi_path):
                    # Comprueba si el track_id ya está en la caché de verificación
                    if track_id in verification_cache:
                        verification_results = verification_cache[track_id]
                    else:
                        # Inicializar una lista para almacenar los resultados de verificación
                        verification_results = []

                        # Iterar a través de la base de datos de caras conocidas
                        for db_image_path in database_dir:
                            # Realizar la verificación facial con DeepFace para cada imagen en la base de datos
                            # Usar los archivos temporales creados
                            verification_result = DeepFace.verify(img1_path=roi_path, img2_path=db_image_path,
                                                                  enforce_detection=False)
                            verification_results.append(verification_result)

                        # Almacenar el resultado en la caché de verificación
                        verification_cache[track_id] = verification_results

                    # Eliminar el archivo temporal de la ROI
                    os.remove(roi_path)

                    if track_id in tracker_cache:
                        track_info = tracker_cache[track_id]
                    else:
                        # Inicializar información de seguimiento para el nuevo track_id
                        track_info = {"tracking_time": 0}
                        tracker_cache[track_id] = track_info

                    # Actualizar el tiempo de seguimiento para el track_id
                    track_info["tracking_time"] += 1

                    # Comprobar si la persona es conocida o desconocida
                    min_distance = min(result['distance'] for result in verification_results)

                    # Definir un umbral de compatibilidad
                    umbral_de_compatibilidad = 0.5  # Puedes ajustar este valor según tus necesidades

                    # Comprobar si la persona es conocida o desconocida
                    if min_distance <= umbral_de_compatibilidad:
                        label = f"Conocido ({track_id})"
                        color = (0, 255, 0)
                    else:
                        label = f"Desconocido ({track_id})"
                        color = (0, 0, 255)

                        # Guardar la imagen de la persona desconocida
                        unknown_person_image_path = os.path.join(unknown_persons_dir, f"persona_desconocida_{track_id}.jpg")
                        cv2.imwrite(unknown_person_image_path, roi)

                    cv2.putText(img=frame, text=label, org=(xmin, ymin - 10),
                                fontFace=cv2.FONT_HERSHEY_PLAIN,
                                fontScale=1.0, color=color, thickness=2)

                    cv2.rectangle(img=frame, pt1=(xmin, ymin), pt2=(xmax, ymax), color=color, thickness=2)


        cv2.putText(frame, formatted_datetime, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("CAMARA VIGILANCIA", frame)

        # Verificar si un desconocido ha sido trackeado por más de 10 segundos
        if check_unknown_person_tracking(tracker_cache, max_tracking_time=10):
            # Enviar un mensaje por WhatsApp una vez
            if not unknown_person_detected:
                phone_number = "+51953053935"  # Reemplaza con el número de teléfono al que deseas enviar el mensaje
                message = "Persona desconocida detectada por más de 10 segundos"
                image_paths = [os.path.join(unknown_persons_dir, filename) for filename in
                               os.listdir(unknown_persons_dir)]

                send_whatsapp_message(phone_number, message, image_paths)
                unknown_person_detected = True

                # Restablecer el temporizador y eliminar la entrada en tracker_cache
                unknown_person_timer = 0
                for track_id in list(tracker_cache.keys()):
                    del tracker_cache[track_id]

            # Incrementar el temporizador para personas desconocidas
        if unknown_person_detected:
            unknown_person_timer += 1
            # Si el temporizador alcanza un cierto valor, restablecer unknown_person_detected
            if unknown_person_timer >= 600:  # 10 segundos * 60 = 600
                unknown_person_detected = False
                unknown_person_timer = 0

    cap.release()
    cv2.destroyAllWindows()
    pass


def VerificacionSesion():
    cap = cv2.VideoCapture(0)

    DeepFace.stream(db_path="database")

    while True:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()  # Libera la cámara
    cv2.destroyAllWindows()  # Cierra las ventanas de OpenCV


# # Iniciar el procesamiento de OpenCV en segundo plano
# opencv_thread = threading.Thread(target=opencv_processing)
# opencv_thread.start()

# resultado = switch.get(opcion, lambda: "Opción no válida")()
# pip install deepface opencv-python-headless

