import numpy as np
import cv2
from ultralytics import YOLO
from sort import Sort
import datetime

tipoVideo = "prueba/ejemplo1_corte.mp4"
confi = 0.3
clase = [0]


def run1():
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

        key = cv2.waitKey(1)

        if key == 27:
            break
        elif key == 32:
            paused = not paused

    print("Eso es todo")
    cap.release()
    cv2.destroyAllWindows()


def run2():
    cap = cv2.VideoCapture(tipoVideo)

    model = YOLO("yolov8n.pt")

    tracker = Sort()

    while cap.isOpened():
        status, frame = cap.read()

        if not status:
            break

        results = model(frame, stream=True)

        for res in results:
            filtered_indices = np.where(res.boxes.conf.cpu().numpy() > 0.5)[0]
            boxes = res.boxes.xyxy.cpu().numpy()[filtered_indices].astype(int)
            tracks = tracker.update(boxes)
            tracks = tracks.astype(int)

            for xmin, ymin, xmax, ymax, track_id in tracks:
                cv2.putText(img=frame, text=f"Id: {track_id}", org=(xmin, ymin - 10), fontFace=cv2.FONT_HERSHEY_PLAIN,
                             fontScale=2, color=(0, 255, 0), thickness=2)
                cv2.rectangle(img=frame, pt1=(xmin, ymin), pt2=(xmax, ymax), color=(0, 255, 0), thickness=2)

            # frame = results[0].plot()

        cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()

opcion = input("Ingrese opcion : ")

switch = {
    "1": run1,
    "2": run2
}


resultado = switch.get(opcion, lambda: "Opción no válida")()