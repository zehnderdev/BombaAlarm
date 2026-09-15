import cv2
import os
import threading
from urllib.parse import quote
from dotenv import load_dotenv
from flask import Flask,Response,render_template
from detect import detect
load_dotenv()

username = os.getenv("CAMERA_USERNAME")
password = quote(os.getenv("CAMERA_PASSWORD", ""), safe="")
ip = os.getenv("CAMERA_IP")
port = os.getenv("CAMERA_RTSP_PORT", "554")

url = f"rtsp://{username}:{password}@{ip}:{port}/h264Preview_01_main"

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    raise RuntimeError("Camera opening error")

print("Connected to Camera")

latest_frame = None
frame_lock = threading.Lock()
running = True

def camera_reader():
    global latest_frame
    while running:
        ret, frame = cap.read()

        if not ret:
            print("Camera read failed")
            continue

        with frame_lock:
            latest_frame = frame


camera_thread = threading.Thread(target=camera_reader , daemon=True)
camera_thread.start()

app = Flask("BombaAlarm")


def generate_frames():
    while True:

        with frame_lock:
            if latest_frame is None:
                continue

            frame = latest_frame.copy()

        frame = detect(frame)

        _, buffer = cv2.imencode(".jpg", frame)

        yield (b"--frame\r\n"b"Content-Type: image/jpeg\r\n\r\n"+ buffer.tobytes()+ b"\r\n")

@app.route("/")
def index():
   return render_template("index.html")


@app.route("/video")
def video():
    response = Response(generate_frames(),mimetype="multipart/x-mixed-replace; boundary=frame")

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Accel-Buffering"] = "no"

    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,threaded="true")