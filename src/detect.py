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
    110,  # x1
    270,  # y1
    500,  # x2
    460,  # y2
)

def is_in_bed(x, y):
    x1, y1, x2, y2 = BED_ZONE

    return x1 <= x <= x2 and y1 <= y <= y2
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    raise RuntimeError("Camera opening error")

print("Connected to Camera")

def detect(frame):
    results = model(frame)
    return results[0].plot()
    
# while True:
#     ret, frame = cap.read()

#     if not ret:
#         print("Got no frame")
#         break

#     results = model(frame)

#     for result in results:
#         for box in result.boxes:
#             class_id = int(box.cls[0])
#             confidence = float(box.conf[0])

#             if class_id != 0:
#                 continue

#             x1, y1, x2, y2 = box.xyxy[0]

#             x1 = int(x1)
#             y1 = int(y1)
#             x2 = int(x2)
#             y2 = int(y2)

#             center_x = (x1 + x2) // 2
#             center_y = (y1 + y2) // 2

#             if is_in_bed(center_x,center_y):
#                 print("IN_BED")
#             else:
#                 print("OUT OF BED")
            
#             print(
#                 f"Person: "
#                 f"confidence={confidence:.2f}, "
#                 f"center=({center_x}, {center_y})"
#             )
# cap.release()