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

