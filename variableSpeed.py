import time
time1 = time.time()
import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
import RPi.GPIO as GPIO


def forward(varLeft, varRight, pwma, pwmb, direction):
    pwma.start(50)
    pwmb.start(50)
    print("left: " ,varLeft)
    print("right: " ,varRight)

    if(direction == "up"):
        GPIO.output(AIN1,1)
        GPIO.output(AIN2,0)
        GPIO.output(BIN1,1)
        GPIO.output(BIN2,0)
    elif(direction == "down"):
        GPIO.output(AIN1,0)
        GPIO.output(AIN2,1)
        GPIO.output(BIN1,0)
        GPIO.output(BIN2,1)
    pwma.ChangeFrequency(varRight)
    pwmb.ChangeFrequency(varLeft)
    sleep(1)
    
if __name__ == '__main__':

    #Motor driver pins
    PWMA = 17
    AIN1 = 22
    AIN2 = 27
    PWMB = 13
    BIN1 = 5
    BIN2 = 6
    STNBY = 18

    #default motor speed
    varLeft = 1000
    varRight = 2000
    direction = "up"

    GPIO.setwarnings(False) # no gpio wanrings
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PWMA, GPIO.OUT)
    GPIO.setup(AIN1, GPIO.OUT)
    GPIO.setup(AIN2, GPIO.OUT)
    GPIO.setup(PWMB, GPIO.OUT)
    GPIO.setup(BIN1, GPIO.OUT)
    GPIO.setup(BIN2, GPIO.OUT)
    GPIO.setup(STNBY, GPIO.OUT)

    pwma = GPIO.PWM(PWMA,1) # pulse width of 1000 Hz
    pwmb = GPIO.PWM(PWMB,1) # pulse width of 1000 Hz
    pwma.start(0)
    pwmb.start(0)

    #initialise motor driver to 0
##    GPIO.output(PWMA,0)
    GPIO.output(AIN1,0)
    GPIO.output(AIN2,0)
##    GPIO.output(PWMB,0)
    GPIO.output(BIN1,0)
    GPIO.output(BIN2,0)
    GPIO.output(STNBY,1)

    blue = (0,0,0)

    cameraHeight = 480
    cameraWidth = 640
    
    middleBottom = (int(cameraWidth/2),int(cameraHeight))
    middleTop = (int(cameraWidth/2),int(cameraHeight-cameraHeight))
    
    # camera settings
    setResolution = (cameraWidth,cameraHeight)
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
#
#        output = image.copy()
#        
        image = cv2.line(image, middleBottom, middleTop, blue, 5)
#
#        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
#        canny_image = cv2.Canny(gray_image, 300, 500)
#        
#        cropImage = regionOfInterest(canny_image, np.array([roi_vertices],np.int32),)
##        detectColor = colorOfInterest(cropImage, lower_red, upper_red)
##        cv2.addWeighted(detectColor, 0.5, image, 0.5 , 0.0, output)
        
        # show frame
        cv2.imshow("Image", image)
#        cv2.imshow("Crop", cropImage)
##        cv2.imshow("Color", detectColor)
                
        # clear stream in preparation for next frame
        rawCapture.truncate(0)
        
        # wait for input
        key = cv2.waitKey(1) & 0xFF
        
        if key == 82:
            print ('up')
            direction = "up"
            print("left: " ,varLeft)
            print("right: " ,varRight)
            
        if key == 84:
            print ('down')
            direction = "down"
            print("left: " ,varLeft)
            print("right: " ,varRight)
            sleep(0.01)

        if key & 0xFF == ord("t"):
            varLeft += 100
            print("left: " + "%.1f" %varLeft)
            print("right: " + "%.1f" %varRight)
            
        if key & 0xFF == ord("g"):
            varLeft -= 100
            print("left: " + "%.1f" %varLeft)
            print("right: " + "%.1f" %varRight)
            
        if key & 0xFF == ord("y"):
            varRight += 100
            print("left: " + "%.1f" %varLeft)
            print("right: " + "%.1f" %varRight)
            
        if key & 0xFF == ord("h"):
            varRight -= 100
            print("left: " + "%.1f" %varLeft)
            print("right: " + "%.1f" %varRight)
            
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
        forward(varLeft, varRight, pwma, pwmb, direction)
        print("forwarding")
            
    time2 = time.time()
    print ('Elapsed time : ', time2-time1,'secs')
    GPIO.cleanup() #important to have to reset the GPIOs
