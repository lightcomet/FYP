import time
time1 = time.time()
import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO

if __name__ == '__main__':

    PWMA = 17
    AIN1 = 22
    AIN2 = 27
    PWMB = 13
    BIN1 = 5
    BIN2 = 6

    GPIO.setwarnings(False) # no gpio wanrings
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PWMA, GPIO.OUT)
    GPIO.setup(AIN1, GPIO.OUT)
    GPIO.setup(AIN2, GPIO.OUT)
    GPIO.setup(PWMB, GPIO.OUT)
    GPIO.setup(BIN1, GPIO.OUT)
    GPIO.setup(BIN2, GPIO.OUT)

    pwma = GPIO.PWM(PWMA,100) # pulse width of 70
    pwmb = GPIO.PWM(PWMB,100) # pulse width of 70

    GPIO.output(PWMA,0)
    GPIO.output(AIN1,0)
    GPIO.output(AIN2,0)
    GPIO.output(PWMB,0)
    GPIO.output(BIN1,0)
    GPIO.output(BIN2,0)

    # colour settings
    blue = (255,0,0)
    # cardboard color
    lower_red = np.array([130,60,60])
    upper_red = np.array([170,255,255])

    # masking settings
    x = 50
    y = 200
    w = 540
    h = 250

    # camera settings
    setResolution = (640,480)
    camera = PiCamera()
    camera.resolution = setResolution
    camera.exposure_mode = 'antishake'
    camera.framerate = 60
    rawCapture = PiRGBArray(camera, size=setResolution)

    # set up time
    time3 = time.time()
    print ('Set up time : ', time3-time1,'secs')

    # camera warm up
    time.sleep(2)

    # capture frames from camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            
        # image array, try do processing here?
        image = frame.array

        # blur
##        blur = cv2.GaussianBlur(image,(5,5),0)
##
##        # vertical line as a reference for path
##        cv2.line(blur,(320,0),(320,640),blue,2) #blue line of width 2, from top middle to bottom middle
##
##        # horizontal line as a reference for path
##        cv2.line(blur,(0,300),(640,300),blue,2) #blue line of width 2, from left to right @ 300
##
##        # horizontal line as a reference for path
##        cv2.line(blur,(0,350),(640,350),blue,2) #blue line of width 2, from left to right @ 350
##
##        # horizontal line as a reference for path
##        cv2.line(blur,(0,400),(640,400),blue,2) #blue line of width 2, from left to right @ 400
        
##        # mask the image 1st
##        mask = np.zeros(blur.shape,np.uint8)
##        mask[y:y+h,x:x+w] = blur[y:y+h,x:x+w]
##
        # finding edges
##        edges = cv2.Canny(blur, 100 ,110)
##
##        # draw contours
##        (_,cnts, hierarchy) = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
##        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
##        for c in cnts:
##            peri = cv2.arcLength(c, True)
##            approx = cv2.approxPolyDP(c, 0.1*peri, True)
##        contour = cv2.drawContours(edges, cnts, -1 , (255,135,0), 3)

        hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_red, upper_red)
        res = cv2.bitwise_and(image,image, mask = mask)
        
        # show frame
        cv2.imshow("Image", image)
                
        # clear stream in preparation for next frame
        rawCapture.truncate(0)
        
        # wait for input
        key = cv2.waitKey(1) & 0xFF
        
        if key == 82:
            print ('up')
##            GPIO.output(PWMA,1)
            pwma.start(40)
            GPIO.output(AIN1,1)
            GPIO.output(AIN2,0)
##            GPIO.output(PWMB,1)
            pwmb.start(40)
            GPIO.output(BIN1,1)
            GPIO.output(BIN2,0)
            
        if key == 84:
            print ('down')
##            GPIO.output(PWMA,1)
            pwma.start(40)
            GPIO.output(AIN1,0)
            GPIO.output(AIN2,1)
##            GPIO.output(PWMB,1)
            pwmb.start(40)
            GPIO.output(BIN1,0)
            GPIO.output(BIN2,1)
            
        if key == 81:
            print ('left')
##            GPIO.output(PWMA,1)
            pwma.start(40)
            GPIO.output(AIN1,1)
            GPIO.output(AIN2,0)
##            GPIO.output(PWMB,1)
            pwmb.start(40)
            GPIO.output(BIN1,0)
            GPIO.output(BIN2,0)
            
        if key == 83:
            print ('right')
##            GPIO.output(PWMA,1)
            pwma.start(40)
            GPIO.output(AIN1,0)
            GPIO.output(AIN2,0)
##            GPIO.output(PWMB,1)
            pwmb.start(40)
            GPIO.output(BIN1,1)
            GPIO.output(BIN2,0)
        
        # stop movement if keyboard p is pressed
        if key & 0xFF == ord("p"):
            print('pause')
            pwma.stop()
            pwmb.stop()

        # exit from loop if keyboard q is pressed
        if key & 0xFF == ord("q"):
            print('quit')
            pwma.stop()
            pwmb.stop()
            break
        
    ##camera.resolution = (640,480)
    ####camera.exposure_mode = 'sports'
    ##camera.exposure_mode = 'antishake' #quite ideal
    ##camera.capture('image.jpg')
    print(res.dtype)
    print(res.shape)
    time2 = time.time()
    print ('Elapsed time : ', time2-time1,'secs')
    GPIO.cleanup() #important to have to reset the GPIOs
