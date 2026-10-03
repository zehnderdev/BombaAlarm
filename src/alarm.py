import os
import requests
import time
from dotenv import load_dotenv



class Alarm:
    def __init__(self):
        self.ip = os.getenv("CAMERA_IP")
        self.username = os.getenv("CAMERA_USERNAME")
        self.password = os.getenv("CAMERA_PASSWORD")
        self.active = False

    def _send(self):
        url = f"https://{self.ip}/cgi-bin/api.cgi"

        params = {
            "user": self.username,
            "password": self.password
        }

        payload = [{
            "cmd": "AudioAlarmPlay",
            "action": 0,
            "param": {
                "channel": 0,
                "alarm_mode": "times",
                "times": 5  # around 2 sec each
            }
        }]

        try:
            response = requests.post(
                url,
                params=params,
                json=payload,
                verify=False,
                timeout=3
            )

            response.raise_for_status()

        except requests.RequestException as e:
            print(f"Alarm request failed: {e}")

    def start(self):
        if self.active:
            return

        self._send()
        self.active = True
        print("Alarm started")

    def stop(self):
        if not self.active:
            return
        # could add something here
        self.active = False
        print("Alarm stopped")

    def update(self, state):
        if state == "IN BED":
            self.start()

        elif state == "OUT OF BED":
            self.stop()

        return self.active
    def getState(self):
        return self.active
