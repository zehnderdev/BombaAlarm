import cv2
from ultralytics import YOLO
import numpy as np

model = YOLO("models/yolo26n-pose.pt") #safe in models folder 

debug = True    
BED_ZONE_LOW = (
    (210,230),  # top left
    (495,228),  # top right
    (495,375),  # bottom right
    (150,330),  # bottom left
)
BED_ZONE_HIGH = (
    (640,844),  # top left
    (2191,750),  # top right
    (2344,1411),  # bottom right
    (479,1496),  # bottom left
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

def avg(*args):
    return sum(args)/ len(args)
        

def is_lying(keypoints, confidence):
    # don´t take legs not very visible in bed
    # take min conf
    shoulder_conf = min(float(confidence[5]),float(confidence[6]))
    hip_conf = min(float(confidence[11]),float(confidence[12]))

    if shoulder_conf < 0.5 or hip_conf < 0.5:
        return False

    shoulder_x = avg(float(keypoints[5][0]),float(keypoints[6][0]))
    shoulder_y = avg(float(keypoints[5][1]),float(keypoints[6][1]))

    hip_x = avg(float(keypoints[11][0]) ,float(keypoints[12][0]))
    hip_y = avg(float(keypoints[11][1]) ,float(keypoints[12][1]))
    # comp angle from arctan
    
    angle = np.degrees(np.arctan2(abs(hip_y - shoulder_y), abs(hip_x - shoulder_x)))

    return angle < 45


def detect(frame):
    results = model(frame,device=0,verbose=False)
    frame = results[0].plot()

    points = np.array(BED_ZONE_HIGH, np.int32)
    cv2.polylines(frame, [points], True, (255, 0, 0), 2)

    in_bed = False

    for result in results:
        for keypoints ,conf in zip( result.keypoints.xy,result.keypoints.conf):

            lying = is_lying(keypoints,conf)

            # if lying and in bed we 
            if lying:
                hip_x = avg(float(keypoints[11][0]),float(keypoints[12][0])) 

                hip_y = avg(float(keypoints[11][1]),float(keypoints[12][1])) 

                if is_in_bed(hip_x, hip_y):
                    in_bed = True
                    state = "IN BED"
                    color = (0, 0, 255)
                else:
                    state = "UNKNOWN"
                    color = (0, 255, 255)
            else:
                state = "OUT OF BED"
                color = (0, 255, 0)

            cv2.putText(frame,state,(50, 100),cv2.FONT_HERSHEY_SIMPLEX,2,color,3)
            # for i, point in enumerate(keypoints):

                # relevant_points = [5, 6, 11, 12]

                # in_bed = 0
                # for i in relevant_points:
                #     if float(conf[i]) < 0.5:
                #         continue

                #     x, y = map(int, keypoints[i])

                #     if is_in_bed(x, y):
                #         in_bed += 1

                # if in_bed >= 2:
                #     state = "IN BED"
                #     color = (0, 0, 255)
                # else:
                #     state = "OUT OF BED"
                #     color = (0, 255, 0)
                #     x, y = map(int, point)
                

                
                # name = keypoint_names[i]
                # if debug:
                #     cv2.circle(frame,(x, y),5,(0, 255, 255),-1)
                #     cv2.putText(frame,f"{i}: {name}",(x + 10, y),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0, 255, 255),2)
               
            # if is_in_bed(center_x, center_y):
            #     state = "IN BED"
            #     color = (0, 0, 255)
            # else:
            #     state = "OUT OF BED"
            #     color = (0, 255, 0)

            

    return frame, in_bed

