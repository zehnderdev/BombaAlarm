import cv2
from ultralytics import YOLO
import numpy as np

model = YOLO("models/yolo26n-pose.pt",verbose="true") #safe in models folder 


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

def is_in_bed(x, y):
    points = np.array(BED_ZONE_HIGH, np.float32)

    return cv2.pointPolygonTest(points,(float(x), float(y)),False) >= 0


def detect(frame):
    results = model(frame,device=0)
    frame = results[0].plot()

    points = np.array(BED_ZONE_HIGH, np.int32)
    cv2.polylines(frame, [points], True, (255, 0, 0), 2)

    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) != 0:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            if is_in_bed(center_x, center_y):
                state = "IN BED"
                color = (0, 0, 255)
            else:
                state = "OUT OF BED"
                color = (0, 255, 0)

            cv2.putText(frame,state,(x1, y1 - 100),cv2.FONT_HERSHEY_SIMPLEX,2,color,2)

    return frame

