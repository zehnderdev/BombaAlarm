import cv2
from ultralytics import YOLO
import numpy as np

model = YOLO("models/yolo26n-pose.pt",verbose="true") #safe in models folder 

debug = True    
BED_ZONE_LOW = (
    (210,230),  # top left
    (495,228),  # top right
    (495,375),  # bottom right
    (150,330),  # bottom left
)
BED_ZONE_HIGH = (
    (1000,1120),  # top left
    (2086,1240),  # top right
    (2007,1854),  # bottom right
    (670,1525),  # bottom left
)

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

def is_in_bed(x, y):
    points = np.array(BED_ZONE_HIGH, np.float32)

    return cv2.pointPolygonTest(points,(float(x), float(y)),False) >= 0


def detect(frame):
    results = model(frame,device=0)
    frame = results[0].plot()

    points = np.array(BED_ZONE_HIGH, np.int32)
    cv2.polylines(frame, [points], True, (255, 0, 0), 2)

    for result in results:
        for keypoints ,conf in zip( result.keypoints.xy,result.keypoints.conf):
            for i, point in enumerate(keypoints):
                x, y = map(int, point)
                confidence = float(conf[i])

                if confidence < 0.5:
                    continue

                if x == 0 and y == 0:
                    continue

                name = keypoint_names[i]
                if debug:
                    cv2.circle(frame,(x, y),5,(0, 255, 255),-1)
                    cv2.putText(frame,f"{i}: {name}",(x + 10, y),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0, 255, 255),2)
               
            # if is_in_bed(center_x, center_y):
            #     state = "IN BED"
            #     color = (0, 0, 255)
            # else:
            #     state = "OUT OF BED"
            #     color = (0, 255, 0)

            

    return frame

