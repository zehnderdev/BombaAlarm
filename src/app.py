import cv2
import os
from urllib.parse import quote
from dotenv import load_dotenv
from flask import Flask,Response,render_template
from detect import detect
load_dotenv()

username = os.getenv("CAMERA_USERNAME")
password = quote(os.getenv("CAMERA_PASSWORD", ""), safe="")
ip = os.getenv("CAMERA_IP")
port = os.getenv("CAMERA_RTSP_PORT", "554")

url = f"rtsp://{username}:{password}@{ip}:{port}/h264Preview_01_sub"

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    raise RuntimeError("Camera opening error")

print("Connected to Camera")

app = Flask("BombaAlarm")


def generate_frames():
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = detect(frame)
        
        _, buffer = cv2.imencode(".jpg", frame)

        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"

@app.route("/")
def index():
   return render_template("index.html")


@app.route("/video")
def video():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)