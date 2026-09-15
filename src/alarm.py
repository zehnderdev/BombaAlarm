import os
import requests
from dotenv import load_dotenv



class Alarm:
    def __init__(self):
        self.ip = os.getenv("CAMERA_IP")
        self.username = os.getenv("CAMERA_USERNAME")
        self.password = os.getenv("CAMERA_PASSWORD")
        self.active = False

    def _send(self, manual_switch):
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
                "times": 10  # around 2 sec each
            }
        }]

        response = requests.post(
            url,
            params=params,
            json=payload,
            verify=False,
            timeout=3
        )

        response.raise_for_status()
        result = response.json()

        if result[0]["code"] != 0:
            raise RuntimeError(f"Camera alarm error: {result}")

    def start(self):
        if self.active:
            return

        self._send(1)
        self.active = True
        print("Alarm started")

    def stop(self):
        if not self.active:
            return

        self._send(0)
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