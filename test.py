import cv2
import os
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("CAMERA_USERNAME")
password = os.getenv("CAMERA_PASSWORD")
ip = os.getenv("CAMERA_IP")
port = os.getenv("RTSP_PORT", "554") # standard RTSP

if not username or not password or not ip:
    raise RuntimeError("Error in env")

password = quote(password, safe="") # url with special characters

url = f"rtsp://{username}:{password}@{ip}:{port}/h264Preview_01_sub"

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    raise RuntimeError("Camera opening error")

print("Connected")

for i in range(10):
    ret, frame = cap.read()

    if not ret:
        print("Got no frame")
        break

    print(f"Frame {i + 1} : {frame.shape}")

cap.release()
