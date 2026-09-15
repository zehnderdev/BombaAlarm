import cv2
import os
from urllib.parse import quote
from dotenv import load_dotenv
from ultralytics import YOLO
import numpy as np

load_dotenv()

username = os.getenv("CAMERA_USERNAME")
password = quote(os.getenv("CAMERA_PASSWORD", ""), safe="")
ip = os.getenv("CAMERA_IP")
port = os.getenv("CAMERA_RTSP_PORT", "554")

url = f"rtsp://{username}:{password}@{ip}:{port}/h264Preview_01_sub"

model = YOLO("models/yolo26n-pose.pt",verbose="true") #safe in models folder 

keypoint_names = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
]

BED_ZONE = (
    (210,230),  # top left
    (495,228),  # top right
    (495,375),  # bottom right
    (150,330),  # bottom left
)

def is_in_bed(x, y):
    points = np.array(BED_ZONE, np.float32)

    return cv2.pointPolygonTest(points,(float(x), float(y)),False) >= 0


def detect(frame):
    results = model(frame,device=0)
    frame = results[0].plot()

    points = np.array(BED_ZONE, np.int32)
    cv2.polylines(frame, [points], True, (255, 0, 0), 2)

    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) != 0:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            if is_in_bed(center_x, center_y):
                state = "IN BED"
            else:
                state = "OUT OF BED"

            cv2.putText(frame,state,(x1, y1 - 10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0, 255, 0),2)

    return frame


# import time

# while True:
#     start = time.time()

#     ret, frame = cap.read()
#     camera_time = time.time()

#     results = model(frame)
#     yolo_time = time.time()

#     frame = results[0].plot()

#     _, buffer = cv2.imencode(".jpg", frame)
#     encode_time = time.time()

#     print(
#         f"camera={camera_time-start:.3f}s "
#         f"yolo={yolo_time-camera_time:.3f}s "
#         f"encode={encode_time-yolo_time:.3f}s"
#     )