import cv2
import os
from urllib.parse import quote
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

username = os.getenv("CAMERA_USERNAME")
password = quote(os.getenv("CAMERA_PASSWORD", ""), safe="")
ip = os.getenv("CAMERA_IP")
port = os.getenv("CAMERA_RTSP_PORT", "554")

url = f"rtsp://{username}:{password}@{ip}:{port}/h264Preview_01_sub"

model = YOLO("models/yolo26n.pt",verbose="true") #safe in models folder 

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    raise RuntimeError("Camera opening error")

print("Connected to Camera")


while True:
    ret, frame = cap.read()

    if not ret:
        print("Got no frame")
        break

    results = model(frame)

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id == 0:
                print(f"Person detected ({confidence:.2f})")

cap.release()