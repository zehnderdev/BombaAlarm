import cv2
import threading
import time
from flask import Flask,Response,render_template

from detect import detect
from camera import read
from state import BedState
from alarm import Alarm

app = Flask("BombaAlarm")


latest_frame = None
frame_lock = threading.Lock()
running = True

bed_state = BedState(duration=20,threshold=0.8)
alarm = Alarm()
def camera_reader():
    global latest_frame
    while running:
        frame = read()


        with frame_lock:
            latest_frame = frame


camera_thread = threading.Thread(target=camera_reader , daemon=True)
camera_thread.start()


monitoring = False
monitoring_lock = threading.Lock()

MEASUREMENT_DURATION = 10
MEASUREMENT_INTERVAL = 1 * 10
MEASUREMENT_RETRY = 3

def monitoring_loop():
    global monitoring
    retries = MEASUREMENT_RETRY
    print("Monitoring loop started")

    while retries>0:
        
        # reset
        bed_state.reset()

        # 10 Sekunden messen
        start_time = time.monotonic()

        while time.monotonic() - start_time < MEASUREMENT_DURATION:

            with frame_lock:
                if latest_frame is None:
                    continue

                frame = latest_frame.copy()

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

@app.route("/start-monitoring", methods=["POST"])
def start_monitoring():
    global monitoring

    with monitoring_lock:

        if monitoring:
            return {
                "status": "already_running"
            }

        monitoring = True

    thread = threading.Thread(
        target=monitoring_loop,
        daemon=True
    )

    thread.start()

    print("Monitoring started by phone")

    return {
        "status": "started"
    }

def generate_frames():
    while True:

        with frame_lock:
            if latest_frame is None:
                continue

            frame = latest_frame.copy()

        frame, in_bed = detect(frame)

        curr_state = bed_state.update(in_bed)
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
    app.run(host="0.0.0.0", port=5000,threaded=True)