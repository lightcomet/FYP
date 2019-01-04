import time
time1 = time.time()
import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
from settings import config

def autoCanny (image, sigma = 0.33):
    # compute the median of the single channel pixel intensities
    median = np.median(image)
    
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * median))
    upper = int(min(255, (1.0 + sigma) * median))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged
    

if __name__ == '__main__':

    settings = config()

    GPIO.setwarnings(False) # no gpio wanrings
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(settings["PWMA"], GPIO.OUT)
    GPIO.setup(settings["AIN1"], GPIO.OUT)
    GPIO.setup(settings["AIN2"], GPIO.OUT)
    GPIO.setup(settings["PWMB"], GPIO.OUT)
    GPIO.setup(settings["BIN1"], GPIO.OUT)
    GPIO.setup(settings["BIN2"], GPIO.OUT)
    GPIO.setup(settings["STNBY"], GPIO.OUT)

    pwma = GPIO.PWM(settings["PWMA"],settings["PWMA_PW"]) # pulse width of 100 Hz
    pwmb = GPIO.PWM(settings["PWMB"],settings["PWMB_PW"]) # pulse width of 100 Hz

    GPIO.output(settings["PWMA"],0)
    GPIO.output(settings["AIN1"],0)
    GPIO.output(settings["AIN2"],0)
    GPIO.output(settings["PWMB"],0)
    GPIO.output(settings["BIN1"],0)
    GPIO.output(settings["BIN2"],0)


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

    font = cv2.FONT_HERSHEY_SIMPLEX

    # camera warm up
    time.sleep(2)

    # capture frames from camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

        pathXList = []
        pathList = []
        pathFilteredList = []
        pathDiffList = []
        pathIndex = []
            
        # image array, processing is done here
        image = frame.array

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        edges = autoCanny(hsv) #settings["cannyMin"] , settings["cannyMax"]

        lines = cv2.HoughLinesP(edges, rho = 1, theta = np.pi/360, threshold =  100, minLineLength = settings["minLineLength"], maxLineGap = settings["maxLineGap"])
        timeStart = time.time()
        if(lines is not None):
            for line in lines:
                for x1,y1,x2,y2 in line:
                    pathXList.extend([x1,x2])
                    print("x1: ",x1, "| y1: ", y1, "| x2: ",x2, "| y2: ",y2)
##                    cv2.line(image,(x1,y1),(x2,y2),(0,255,0),2)
##                    cv2.putText(image, str(x1)+ "|"+str(y1)+"|"+str(x2)+"|"+str(y2),(x1-20,y1+20), font, 1, (255,255,255),2,cv2.LINE_AA)
            pathList.sort()

        pathXList = list(set(pathXList))
        pathXList.sort()
        print("pathXList : ",pathXList)
        print("length of pathXlist : ",len(pathXList))
        i = 0
        while i < len(pathXList):
##            print("i : ", i)
            if(i == 0):
                pass   
            else:
                if(pathXList[i] - pathXList[i-1] <= 30):
                    average = (pathXList[i] + pathXList[i-1])//2
##                    print(average," index:",i)
                    del pathXList[i]
                    del pathXList[i-1]
                    pathXList.insert(i-1,average)
##                    print(pathXList)
                    i-= 1
                else:
                    pass
            i+= 1
        print("final pathXList : ", pathXList)
        timeStop = time.time()
        print("time taken : ",(timeStop-timeStart)*1000, "ms")
        left = pathXList[0]
        right = pathXList[1]
        if(250 <= left and right <= 400):
            print("forward")
        elif(right > 401):
            print("right")
        elif(left<249):
            print("left")
        
        # show frame
        cv2.imshow("Image", edges)
        cv2.imshow("Line Image", image)
                
        # clear stream in preparation for next frame
        rawCapture.truncate(0)
        
        # wait for input
        key = cv2.waitKey(1) & 0xFF
        
        if key == 82:
            print ('up')
            # duty cycle of 40%
            pwma.start(40)
            GPIO.output(AIN1,1)
            GPIO.output(AIN2,0)
            
            # duty cycle of 40%
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
        
    time2 = time.time()
    print ('Elapsed time : ', time2-time1,'secs')
    GPIO.cleanup() #important to have to reset the GPIOs
