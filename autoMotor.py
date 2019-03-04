import time
time1 = time.time()
import cv2
import numpy as np
import math
from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
from settings import config

slidingWindow = []
amtToRemove = 0

def movement (varLeft, varRight, moreSide, lessSide, pwma, pwmb, direction, findPath):
    print("left: ", varLeft, " | ", "right: ", varRight, " | ", "direction: ", direction, " | ", "pathFlag: ",findPath)
    if(findPath == True):
        print("finding path")
        print("no path detected")
        pwma.stop()
        pwmb.stop()
##        pwma.start(1)
##        pwmb.start(20)
##        GPIO.output(settings["AIN1"],1)
##        GPIO.output(settings["AIN2"],0)
##        GPIO.output(settings["BIN1"],1)
##        GPIO.output(settings["BIN2"],0)
##        pwma.ChangeFrequency(varRight)
##        pwmb.ChangeFrequency(varLeft)
    else:
        if(direction == "up"):
            print("up movement")
            print("more side : ", moreSide, "less side : ", lessSide)
##            pwma.start(moreSide)
##            pwmb.start(lessSide)
##            GPIO.output(settings["AIN1"],1)
##            GPIO.output(settings["AIN2"],0)
##            GPIO.output(settings["BIN1"],1)
##            GPIO.output(settings["BIN2"],0)
##            pwma.ChangeFrequency(varRight)
##            pwmb.ChangeFrequency(varLeft)
            
        elif(direction == "left"):
            print("left movement")
            print("more side : ", moreSide, "less side : ", lessSide)
##            pwma.start(moreSide)
##            pwmb.start(lessSide)
##            GPIO.output(settings["AIN1"],1)
##            GPIO.output(settings["AIN2"],0)
##            GPIO.output(settings["BIN1"],1)
##            GPIO.output(settings["BIN2"],0)
##            pwma.ChangeFrequency(varRight)
##            pwmb.ChangeFrequency(varLeft)
            
        elif(direction == "right"):
            print("right movement")
            print("more side : ", moreSide, "less side : ", lessSide)
##            pwma.start(lessSide)
##            pwmb.start(moreSide)
##            GPIO.output(settings["AIN1"],1)
##            GPIO.output(settings["AIN2"],0)
##            GPIO.output(settings["BIN1"],1)
##            GPIO.output(settings["BIN2"],0)
##            pwma.ChangeFrequency(varRight)
##            pwmb.ChangeFrequency(varLeft)
    

if __name__ == '__main__':

    settings = config()

    #initialise
    GPIO.setwarnings(False) # no gpio wanrings
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(settings["PWMA"], GPIO.OUT)
    GPIO.setup(settings["AIN1"], GPIO.OUT)
    GPIO.setup(settings["AIN2"], GPIO.OUT)
    GPIO.setup(settings["PWMB"], GPIO.OUT)
    GPIO.setup(settings["BIN1"], GPIO.OUT)
    GPIO.setup(settings["BIN2"], GPIO.OUT)
    GPIO.setup(settings["STNBY"], GPIO.OUT)

##    pwma = GPIO.PWM(settings["PWMA"],settings["PWMA_PW"]) # pulse width of 100 Hz
##    pwmb = GPIO.PWM(settings["PWMB"],settings["PWMB_PW"]) # pulse width of 100 Hz

    GPIO.output(settings["AIN1"],0)
    GPIO.output(settings["AIN2"],0)
    GPIO.output(settings["BIN1"],0)
    GPIO.output(settings["BIN2"],0)
    GPIO.output(settings["STNBY"],1)

    startFlag = False
    direction = False
    pathFlag = False
    varLeft = 1
    varRight = 1

##    pwma = GPIO.PWM(settings["PWMA"],1) # pulse width of 1 Hz
##    pwmb = GPIO.PWM(settings["PWMB"],1) # pulse width of 1 Hz
##    GPIO.output(settings["AIN1"],1)
##    GPIO.output(settings["AIN2"],0)
##    GPIO.output(settings["BIN1"],1)
##    GPIO.output(settings["BIN2"],0)
##    GPIO.output(settings["STNBY"],1)
##    pwma.start(1)
##    pwmb.start(1)

    font = cv2.FONT_HERSHEY_SIMPLEX


    # camera settings
    setResolution = (640,480)
    camera = PiCamera()
    camera.resolution = setResolution
    camera.exposure_mode = 'antishake'
    camera.framerate = 90
    rawCapture = PiRGBArray(camera, size=setResolution)

    # set up time
    time3 = time.time()
    print ('Set up time : ', time3-time1,'secs')

    # camera warm up
    time.sleep(2)

    # capture frames from camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):


        tempWindow = []
        diffInX = []
        diffInCentre = []
        centrePoint = (319,479)
        varLeft = 1000
        varRight = 1250
        leftPointSum = 0
        rightPointSum = 0
        breakPoint = 0
        toRemove = False
            
        # image array, processing is done here
        image = frame.array

        blur = cv2.GaussianBlur(image,(5,5),0)

        hsv = cv2.cvtColor(blur, cv2.COLOR_RGB2GRAY)

        edges = cv2.Canny(hsv, 80, 100)
        
##        lines = cv2.HoughLinesP(edges, rho = 1, theta = np.pi/360, threshold =  100, minLineLength = settings["minLineLength"], maxLineGap = settings["maxLineGap"])
        timeStart = time.time()
        # show frame
        cv2.imshow("Canny Image", edges)
        
        print("--------------------------------------------------------------------------------")

        nonzero = cv2.findNonZero(edges)
        counter = 0
        if(nonzero is not None):
            #appending
            lengthNonZero = len(nonzero)
            print("length of nonzero : ", lengthNonZero)
            for index in range (lengthNonZero-1, 0 , -1):
                if(nonzero[index][0][1] == 479):
                    print("x is : ",nonzero[index][0][0], " y is ", nonzero[index][0][1])
                    tempWindow.append((nonzero[index][0][0],nonzero[index][0][1]))
                    counter += 1
                elif(nonzero[index][0][1] <= 478):
                    print("index to break : ",index)
                    break
            print("tempWindow : ", tempWindow)
            print("counter : ",counter)
            tempWindow.sort(key=lambda k : [k[0],k[1]])
            timeStopAppend = time.time()
            print("time taken to append: ",(timeStopAppend-timeStart)*1000, "ms")
            
            #comparing
            lenTempWindow = len(tempWindow)
            lenSlidingWindow = len(slidingWindow)
            print("temp window length : ", lenTempWindow, "sliding window length : ",lenSlidingWindow)
            if(lenSlidingWindow != 0):
                toRemove = True
                if(lenTempWindow == lenSlidingWindow and lenSlidingWindow == 2): #exactly 2 points
                    for i in range(lenTempWindow):
                        diffX = tempWindow[i][0] - slidingWindow[i][0]
                        diffCentre = tempWindow[i][0] - centrePoint[0]
                        diffInX.append(diffX)
                        diffInCentre.append(diffCentre)
                        print("diff in x : ",diffX, " diff from centre : ",diffCentre, " diffXList : ",diffInX, " diffCentreList : ",diffInCentre)
                    
                elif(lenTempWindow > 2): #reduction of 3 or more points to 2
                    for i in range(lenTempWindow):
                        if(i != 0):
                            diffTemp = tempWindow[i][0] - tempWindow[i-1][0]
                            print("diffTemp",diffTemp)
                            if(diffTemp >= 10):
                                breakPoint = i
                                break
                    print("breakpoint :",breakPoint)
                    for i in range(breakPoint):
                        leftPointSum += tempWindow[i][0]
                    averageLeft = leftPointSum//(breakPoint)
                    for i in range(breakPoint,lenTempWindow):
                        rightPointSum += tempWindow[i][0]
                    averageRight = rightPointSum//(lenTempWindow-breakPoint)
                    print("left : ", averageLeft, "right : ", averageRight)
                    tempWindow = [(averageLeft,479),(averageRight,479)]
                    for i in range(len(tempWindow)):
                        diffX = tempWindow[i][0] - slidingWindow[i][0]
                        diffCentre = tempWindow[i][0] - centrePoint[0]
                        diffInX.append(diffX)
                        diffInCentre.append(diffCentre)
                        print("diff in x : ",diffX, " diff from centre : ",diffCentre, " diffXList : ",diffInX, " diffCentreList : ",diffInCentre)
##                    diffLeftCentre = averageLeft - centrePoint[0]
##                    diffRightCentre = averageRight - centrePoint[0]
##                    diffX = tempWindow[i][0] - slidingWindow[i][0]
                    counter = 2
                        
                elif(lenTempWindow == 1): # 1 points (measure from centre difference?
                    
                    diffCentre = tempWindow[0][0] - centrePoint[0]
                    diffInCentre.append(diffCentre)
                    print(" diff from centre : ",diffCentre, " diffCentreList : ",diffInCentre)
                    tempWindow = []
                    toRemove = False
                else:
                    tempWindow = []
                    toRemove = False
                    
                    
            print("extending sliding with ", tempWindow)
            slidingWindow.extend(tempWindow)
            timeStopCompare = time.time()
            print("time taken to compare: ",(timeStopCompare-timeStart)*1000, "ms")
            #removing
            if(amtToRemove == 0):
                amtToRemove = counter
            else:
                if(toRemove):
                    print("sliding window : ",slidingWindow, " counter : ",amtToRemove)
                    slidingWindow = slidingWindow[amtToRemove:]
                    amtToRemove = counter
                    print("sliding window : ",slidingWindow, " counter : ",amtToRemove)
            
        pathFlag = False
        timeStop = time.time()
        print("time taken to remove: ",(timeStop-timeStart)*1000, "ms")
    
        #controlling
        lenDiffInX = len(diffInX)
        lenDiffInCentre = len(diffInCentre)

        if(lenDiffInX != 0): #left movement is -ve, right movement is  +ve
            diffXValue = max(diffInX)
            print("X value to use : ", diffXValue)
            
        if(lenDiffInCentre != 0):
            diffCentreValue = sum(diffInCentre)/len(diffInCentre)
            print("Centre value to use : ", diffCentreValue)

        if(diffCentreValue < 20 or diffCentreValue > -20):
            
            if(diffXValue < 0):
                #reduce right motor
            elif(diffXValue > 0):
                #increase right motor
            elif(diffXValue == 0):
            
##        pwma.ChangeFrequency(1000)
##        pwmb.ChangeFrequency(1200)
##        pwma.ChangeDutyCycle(20)
##        pwmb.ChangeDutyCycle(20)
        
        # clear stream in preparation for next frame
        rawCapture.truncate(0)
        
        # wait for input
        key = cv2.waitKey(1) & 0xFF

        # stop movement if keyboard p is pressed
        if key & 0xFF == ord("s"):
            print('start')
            startFlag = True
            direction = "up"
        
        # stop movement if keyboard p is pressed
        if key & 0xFF == ord("p"):
            print('pause')
            startFlag = False
            pwma.stop()
            pwmb.stop()

        # exit from loop if keyboard q is pressed
        if key & 0xFF == ord("q"):
            print('quit')
            startFlag = False
##            pwma.stop()
##            pwmb.stop()
            break
        
    time2 = time.time()
    print ('Elapsed time : ', time2-time1,'secs')
    GPIO.cleanup() #important to have to reset the GPIOs
