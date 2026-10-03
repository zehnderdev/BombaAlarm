import cv2
import threading
import time
import json
from flask import Flask, Response, render_template, request, jsonify

from detect import detect
from camera import CameraStream, connect_from_config
from state import BedState
from alarm import Alarm
from config import *

import os
from urllib.parse import quote
from dotenv import load_dotenv

# // INIT // 
load_dotenv()

camera_stream = None
config = load_config()

if config:
    camera_stream = connect_from_config(config)

bed_state = BedState(duration=20,threshold=0.8)
alarm = Alarm()

MEASUREMENT_DURATION = 10
MEASUREMENT_INTERVAL = 1 * 10
MEASUREMENT_RETRY = 3
app = Flask("BombaAlarm")

# // 


@app.route("/setup_camera", methods=["POST"])
def setup_camera():
    global camera_stream
    
    data = request.json

    save_config(data)
    if camera_stream is not None:
        camera_stream.stop()
        camera_stream = None

    camera_stream = connect_from_config(data)
    if camera_stream is None:
        return jsonify({"status": "error", "message": "Failed to connect to camera."}), 400
    
    return jsonify({"status": "ok"})


def monitoring_loop():
    global monitoring


    if camera_stream is None:
        print("Monitoring loop cannot start: Camera stream is not initialized.")
        return
    
    retries = MEASUREMENT_RETRY
    print("Monitoring loop started")

    while retries >0:
        
        # reset
        bed_state.reset()

        # 10 Sekunden messen
        start_time = time.monotonic()

        while time.monotonic() - start_time < MEASUREMENT_DURATION:

            ret, frame = camera_stream.read()

            if not ret or frame is None:
                print("Failed to read frame from camera stream")
                time.sleep(0.1)
                continue
            
            frame, in_bed = detect(frame)

            bed_state.update(in_bed)

            print(f"Monitoring: {in_bed}")

        current_state = bed_state.getState()

        print(f"Measurement result: {current_state}")
 
        alarm.update(current_state) # sleeps for 
        monitoring =alarm.getState()
        if monitoring is True:
            print(f"Sleeping for {MEASUREMENT_INTERVAL} sek")
            time.sleep(MEASUREMENT_INTERVAL)
        else:
            retries -= 1

            
            print(f"{retries}more Retries to deactivate Monitoring loop")


    monitoring = False
    print("Monitoring loop stopped")
    return


def generate_frames():
    while True:

        if camera_stream is None:
            time.sleep(1)
            continue
        ret, frame = camera_stream.read()

        if not ret or frame is None:
            print("Failed to read frame from camera stream")
            time.sleep(0.1)
            continue

        
        frame, in_bed = detect(frame.copy())

        bed_state.update(in_bed)
        curr_state = bed_state.getState()
        alarm_active = alarm.update(curr_state)

        alarm_text = "ALARM" if alarm_active else "NO ALARM"

        cv2.putText(
                    frame,
                    alarm_text,
                    (2150, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (0, 0, 255) if alarm_active else (0, 255, 0),
                    3
                )
        
        frame = cv2.resize(frame, (1920, 1080))
        _, buffer = cv2.imencode(".jpg", frame)

        yield (b"--frame\r\n"b"Content-Type: image/jpeg\r\n\r\n"+ buffer.tobytes()+ b"\r\n")

        time.sleep(0.05)




@app.route("/")
def index():
   config = load_config()
   connected = camera_stream is not None
   return render_template("index.html",ip=config.get("ip", ""),port=config.get("port", ""),username=config.get("username", ""),password=config.get("password", ""),rtsp_url=config.get("rtsp_url", ""),active=connected)


@app.route("/video")
def video():
    if camera_stream is None:
        return "Camera stream not initialized", 503
    response = Response(generate_frames(),mimetype="multipart/x-mixed-replace; boundary=frame")

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Accel-Buffering"] = "no"

    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,threaded=True)