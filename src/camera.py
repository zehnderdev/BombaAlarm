import cv2
import threading
import time
from urllib.parse import quote


class CameraStream:

    def __init__(self,src):
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            print(f"Error: Unable to open video stream from {src}")
            return None
        
        self.ret, self.frame = self.stream.read()
        self.stopped = False

        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True 
        self.thread.start()

    def update(self):
        while not self.stopped:
            if not self.stream.isOpened():
                self.stopped = True
                break

            self.ret, self.frame = self.stream.read()
            time.sleep(0.01)

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.stream.release()    


def connect_from_config(data):
    if data.get("rtsp_url") and data["rtsp_url"].strip() != "":
        url = data["rtsp_url"]
    elif data.get("ip"):
        ip = data.get("ip", "")
        port = data.get("port", "554")
        user = data.get("username", "")
        pw = quote(data.get("password", ""), safe="")
        url = f"rtsp://{user}:{pw}@{ip}:{port}/h264Preview_01_main"
    else:
        return None
    
    print(f"Start Camera through cache: {url}")

    return CameraStream(src=url)