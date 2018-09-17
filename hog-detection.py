import numpy as np
import cv2
import os
import RPi.GPIO as GPIO

from picamera.array import PiRGBArray
from picamera import PiCamera

GPIO.setmode(GPIO.BOARD)
os.system("sudo pigpiod")

# define servos GPIO
panPin = 18
tiltPin = 11

#face_cascade = cv2.CascadeClassifier('haarcascade_upperbody.xml')
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

hog = cv2.HOGDescriptor()
hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector())

#cap = cv2.VideoCapture(0)
cap = PiCamera()
cap.resolution = (320,240)
cap.framerate = 32
#cap.rotation = -180
rawCapture = PiRGBArray(cap, size=(320,240))
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc,20.0,(320,240))

def draw_detections(img, rects, thickness = 1):
      for x,y,w,h in rects :
            pad_w, pad_h = int(0.15*w), int(0.05*h)
            cv2.rectangle(img, (x+pad_w, y+pad_h), (x+w-pad_w,y+h-pad_h), (0,255,255), thickness)


# Defining and initializing globals
global panServoAngle
panServoAngle = 45
global tiltServoAngle
tiltServoAngle = 45

# positioning servos at 105-90 degrees
print("\n [INFO] Positioning servos to initial position ==> Press 'ESC' to quit Program \n")
os.system("python3 servo.py " + str(panPin) + " " + str(panServoAngle))
os.system("python3 servo.py " + str(tiltPin) + " " + str(tiltServoAngle))

# Position servos to capture object at center of screen
def servoPosition (x, y):
#150,120
    global panServoAngle
    global tiltServoAngle
    if (x <130):
        panServoAngle += 10
        if panServoAngle > 140:
            panServoAngle = 140
        os.system("python3 servo.py " + str(panPin) + " " + str(panServoAngle))
  
    if (x > 170):
        panServoAngle -= 10
        if panServoAngle < 40:
            panServoAngle = 40
        os.system("python3 servo.py " + str(panPin) + " " + str(panServoAngle))

    if (y < 100):
        tiltServoAngle += 10
        if tiltServoAngle > 140:
            tiltServoAngle = 140
        os.system("python3 servo.py " + str(tiltPin) + " " + str(tiltServoAngle))
  
    if (y > 140):
        tiltServoAngle -= 10
        if tiltServoAngle < 40:
            tiltServoAngle = 40
        os.system("python3 servo.py " + str(tiltPin) + " " + str(tiltServoAngle))


#while True:
for still in cap.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    img = still.array
    #ret, img = cap.read()
    #cv2.imshow('img',img)
    img = cv2.flip(img, -1)
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = img
    #faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    #faces = face_cascade.detectMultiScale(img,1.01,4,(cv2.CASCADE_DO_CANNY_PRUNING + cv2.CASCADE_FIND_BIGGEST_OBJECT + cv2.CASCADE_DO_ROUGH_SEARCH),(80,80))

    faces,w = hog.detectMultiScale(img, winStride=(8,8), padding=(32,32), scale=1.05)

    out.write(img)

    for (x,y,w,h) in faces:
        servoPosition(320-int(x+w/2), 240-int(y+h/2))
        #servoPosition(int(x+w/2), int(y+h/2))
        pad_w, pad_h = int(0.15*w), int(0.05*h)
        cv2.rectangle(img,(x+pad_w,y+pad_h),(x+w-pad_w,y+h-pad_h),(0,255,255),2)
        #servoPosition(int(x+w/2), int(y+h/2))
        print (int(x+w/2), int(y+h/2))
    cv2.imshow('img',img)
    rawCapture.truncate(0)
    k = cv2.waitKey(1) & 0xff
    if k == ord("q"): # press 'ESC' to quit
        break

# do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff \n")
GPIO.cleanup()
#cap.release()
out.release()
cv2.destroyAllWindows()

