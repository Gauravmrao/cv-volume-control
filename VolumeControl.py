import cv2
import time
import numpy as np
import HandTrackingModule as hand # TODO: import the hand tracking module separately from its own folder
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# define the video input
camWidth = 900
camHeight = 750
cap = cv2.VideoCapture(0)
cap.set(3, camWidth)
cap.set(4, camHeight)
prevTime = 0
currTime = 0

# initialize necessary information for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange() # -65.25 to 0
minVol = volRange[0]
maxVol = volRange[1]
volumeBar = 400


# set up the hand detector
detector = hand.handDetector(detectionConfidence=0.75)

while True:
    success, img = cap.read()

    # use the detector to find the hands and position details
    img = detector.findHands(img)
    landmarks = detector.findPosition(img, draw=False)

    # Volume control flow thumb (4) and the index finger (8)
    if len(landmarks) > 0:
        thumbX = landmarks[4][1]
        thumbY = landmarks[4][2]
        indexX = landmarks[8][1]
        indexY = landmarks[8][2]
        cv2.circle(img, (thumbX, thumbY), 15, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (indexX, indexY), 15, (255, 0, 0), cv2.FILLED)

        # add visual interactions from thumb and index movements
        cv2.line(img, (thumbX, thumbY), (indexX, indexY), (0, 255, 255), 2)
        distance = (((thumbX - indexX) ** 2) + (( thumbY - indexY) ** 2)) ** 0.5
        if distance > 50:
            cv2.circle(img, ((thumbX + indexX) // 2, (thumbY + indexY) // 2), 15, (0, 255, 255), cv2.FILLED)
        else:
            cv2.circle(img, ((thumbX + indexX) // 2, (thumbY + indexY) // 2), 15, (255, 255, 255), cv2.FILLED)
        # print(int(distance))

        # volume changes
        vol = np.interp(distance, [30, 200], [minVol, maxVol])
        volume.SetMasterVolumeLevel(vol, None)
        volumeBar = np.interp(distance, [30, 200], [400, 150])
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3, cv2.FILLED)
    cv2.rectangle(img, (50, int(volumeBar)), (85, 400), (0, 255, 0), -1)


    # calculate and display the FPS
    currTime = time.time()
    fps = 1/(currTime - prevTime)
    prevTime = currTime
    cv2.putText(img, f'FPS: {str(int(fps))}', (10, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)


    cv2.imshow("image", img)
    cv2.waitKey(1)