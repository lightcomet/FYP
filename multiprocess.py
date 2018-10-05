from multiprocessing import Process, Queue
import time

def camera(stopQueue, objectQueue, cameraLeftQueue, cameraRightQueue):
    import time
    time1 = time.time()
    import cv2
    import numpy as np
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    import RPi.GPIO as GPIO
    import csv

    def nothing(x):
        pass

    def distFromCenter (nonZero, lengthOfNonZero):
        criticalY = -1
        total = 0
        count = 0
        
        # retrieve critical Y value and break loop
        for counter in range(0, lengthOfNonZero):
            if(criticalY != -1):
                break
            if(counter == 0):
                prevY = nonZero[counter][0][1]
            else:
                currentY = nonZero[counter][0][1]
                diffY = currentY - prevY
                if(diffY == 0):
                    count = 0
                else:
                    # difference of 1 between previous and current Y
                    if(count == 1):
                        print("critical Y value is: ",prevY)
                        criticalX1 = nonZero[counter-1][0][0]
                        criticalX2 = nonZero[counter-1][0][0]
                        print("critical X value is: ",criticalX1)
                        criticalY = 0
                        indexY = counter - 1 
                        break
                    else:
                        prevY = currentY
                        count += 1

        # only add if X value is within critical range (first half range)
        print(indexY)
        for counter in range(indexY,-1,-1):
            if(criticalY == -1):
                break
            else:
                currentX1 = nonZero[counter][0][0]
                diffX1 = currentX1 - criticalX1
                if(diffX1 >= -3 and diffX1 <= 3):
                    total += currentX1
                    criticalX1 = currentX1

        # only add if X value is within critical range (second half range)
        for counter in range(indexY+1,lengthOfNonZero):
            if(criticalY == -1):
                break
            else:
                currentX2 = nonZero[counter][0][0]
                diffX2 = currentX2 - criticalX2
                if(diffX2 >= -3 and diffX2 <= 3):
                    total += currentX2
                    criticalX2 = currentX2
        return total

    def keyInput (key):
        if key == 82:
            print ('up')
    ##            GPIO.output(PWMA,1)
            pwma.start(varRight)
            GPIO.output(AIN1,1)
            GPIO.output(AIN2,0)
    ##            GPIO.output(PWMB,1)
            pwmb.start(varLeft)
            GPIO.output(BIN1,1)
            GPIO.output(BIN2,0)
            print("left: " ,varLeft)
            print("right: " ,varRight)
            
        if key == 84:
            print ('down')
    ##            GPIO.output(PWMA,1)
            pwma.start(varRight)
            GPIO.output(AIN1,0)
            GPIO.output(AIN2,1)
    ##            GPIO.output(PWMB,1)
            pwmb.start(varLeft)
            GPIO.output(BIN1,0)
            GPIO.output(BIN2,1)
            print("left: " ,varLeft)
            print("right: " ,varRight)

        if key == ord("t"):
            varLeft += 0.1
            print("left: " + "%.1f" %varLeft)
            print("right: " + "%.1f" %varRight)
            
        if key == ord("g"):
            varLeft -= 0.1
            print("left: " + "%.1f" %varLeft)
            print("right: " + "%.1f" %varRight)
            
        if key == ord("y"):
            varRight += 0.1
            print("left: " + "%.1f" %varLeft)
            print("right: " + "%.1f" %varRight)
            
        if key == ord("h"):
            varRight -= 0.1
            print("left: " + "%.1f" %varLeft)
            print("right: " + "%.1f" %varRight)
            
        # stop movement if keyboard p is pressed
        if key == ord("p"):
            print('pause')
            pwma.stop()
            pwmb.stop()

        # exit from loop if keyboard q is pressed
        if key == ord("q"):
            print('quit')
            pwma.stop()
            pwmb.stop()
            nonZeroLeft = cv2.findNonZero(leftMask)
            nonZeroRight = cv2.findNonZero(rightMask)
            
            stopQueue.put_nowait("stop ultrasonic")
            cameraLeftQueue.put_nowait(nonZeroLeft)
            cameraRightQueue.put_nowait(nonZeroRight)
            return True
        return False

    if __name__ == '__main__':

        #Motor driver pins
        PWMA = 17
        AIN1 = 22
        AIN2 = 27
        PWMB = 13
        BIN1 = 5
        BIN2 = 6

        #default motor speed
        varLeft = 35
        varRight = 35

        GPIO.setwarnings(False) # no gpio warnings
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PWMA, GPIO.OUT)
        GPIO.setup(AIN1, GPIO.OUT)
        GPIO.setup(AIN2, GPIO.OUT)
        GPIO.setup(PWMB, GPIO.OUT)
        GPIO.setup(BIN1, GPIO.OUT)
        GPIO.setup(BIN2, GPIO.OUT)

        pwma = GPIO.PWM(PWMA,100) # pulse width of 100
        pwmb = GPIO.PWM(PWMB,100) # pulse width of 100

        #initialise motor driver to 0
        GPIO.output(PWMA,0)
        GPIO.output(AIN1,0)
        GPIO.output(AIN2,0)
        GPIO.output(PWMB,0)
        GPIO.output(BIN1,0)
        GPIO.output(BIN2,0)

        #camera resolution
        cameraHeight = 480
        cameraWidth = 640

        # colour settings
        white = (255,255,255)

        # main logic parameters
        leftX1 = 0
        leftY1 = 0
        leftX2 = 319
        leftY2 = 479

        rightX1 = 320
        rightY1 = 0
        rightX2 = 639
        rightY2 = 479

        dataLeftX = ['Left X Values']
        dataLeftY = ['Left Y Values']
        dataRightX = ['Right X Values']
        dataRightY = ['Right Y Values']

        #coordinate settings
        middleBottom = (int(cameraWidth/2),int(cameraHeight))
        middleTop = (int(cameraWidth/2),int(cameraHeight-cameraHeight))
        print(middleBottom)
        print(middleTop)


        # camera settings
        setResolution = (cameraWidth,cameraHeight)
        camera = PiCamera()
        camera.resolution = setResolution
        camera.exposure_mode = 'antishake'
        camera.framerate = 60
        rawCapture = PiRGBArray(camera, size=setResolution)

        # canny min & max
        cannyMin = 80
        cannyMax = 100

        # set up time
        time3 = time.time()
        print ('Set up time : ', time3-time1,'secs')


        # camera warm up
        time.sleep(2)
        
##        cv2.namedWindow('window')
##        cv2.createTrackbar('Canny Min','window',0,900,nothing)
##        cv2.createTrackbar('Canny Max','window',0,900,nothing)
##        cv2.setTrackbarPos('Canny Min','window',80)
##        cv2.setTrackbarPos('Canny Max','window',100)

        # capture frames from camera
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

##            cannyMin = cv2.getTrackbarPos('Canny Min','window')
##            cannyMax = cv2.getTrackbarPos('Canny Max','window')
            
            # image array, processing done here
            image = frame.array

            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            edges = cv2.Canny(hsv, cannyMin ,cannyMax)

        ##    edges = cv2.line(edges, middleBottom, middleTop, white, 1)

            cv2.imshow('mask',hsv)
        ##    cv2.imshow('edges',edges)

            mask = np.zeros(edges.shape, dtype="uint8")
            cv2.rectangle(mask, (leftX1,leftY1), (leftX2,leftY2),(255,255,255),-1)

            mask2 = np.zeros(edges.shape, dtype="uint8")
            cv2.rectangle(mask2, (rightX1,rightY1), (rightX2,rightY2),(255,255,255),-1)

            leftMask = cv2.bitwise_and(edges,mask)
            rightMask = cv2.bitwise_and(edges,mask2)

            nonZeroLeft = cv2.findNonZero(leftMask) #2nd 0 is 1st array pair, 3rd 0 is 1st item in array
            nonZeroRight = cv2.findNonZero(rightMask) #2nd 0 is 1st array pair, 3rd 0 is 1st item in array
            
            #check if empty
            if(nonZeroLeft is None or nonZeroRight is None):
                pass
            
            else:
                lengthNonZeroLeft = len(nonZeroLeft)
                lengthNonZeroRight = len(nonZeroRight)
                
                print("length of non zero arrray left: ", lengthNonZeroLeft ," length of non zero arrray right: ", lengthNonZeroRight)

                totalLeft = distFromCenter (nonZeroLeft, lengthNonZeroLeft)

                print("total Left: ",totalLeft)
                print("left: ",leftX2 - (totalLeft/cameraHeight))
                totalLeft = 0

                totalRight = distFromCenter (nonZeroRight, lengthNonZeroRight)

                print("total right: ",totalRight)
                print("right: ",(totalRight/cameraHeight)- rightX1)
                totalRight = 0            
            

            # count number of pixels on masked image
        ##    nonZeroLeft = cv2.countNonZero(leftMask)
        ##    nonZeroRight = cv2.countNonZero(rightMask)
            
        ##    print("left: ",nonZeroLeft," right: ",nonZeroRight)
            
            cv2.imshow('mask1',leftMask)
            cv2.imshow('mask2',rightMask)
                    
            # clear stream in preparation for next frame
            rawCapture.truncate(0)
            
            # wait for input
            key = cv2.waitKey(1) & 0xFF
            
            breakLoop = keyInput(key)
            if(breakLoop == True):
                break
            else:
                pass


            if(objectQueue.empty()):
                pass
            else:
                objectFlag = objectQueue.get_nowait()
                print("object queue content: ",objectFlag)
                if(objectFlag == "obstacle"):
                    print("stop car")

                    
        time2 = time.time()
        print ('Elapsed time : ', time2-time1,'secs')
        GPIO.cleanup() #important to have to reset the GPIOs
        


def ultrasonic(stopQueue, objectQueue):
    import time
    import RPi.GPIO as GPIO
    
    GPIO.setwarnings(False) # no gpio warnings
    GPIO.setmode(GPIO.BCM)
    trigger = 26
    echo = 19

    GPIO.setup(trigger, GPIO.OUT)
    GPIO.setup(echo, GPIO.IN)

    obstacleDist = 20.0

    def distance():
        # set Trigger to HIGH
        GPIO.output(trigger, True)
     
        # set Trigger after 10microseconds to LOW
        time.sleep(0.00001)
        GPIO.output(trigger, False)
     
        StartTime = time.time()
        StopTime = time.time()
     
        # save StartTime
        while GPIO.input(echo) == 0:
            StartTime = time.time()
     
        # save time of arrival
        while GPIO.input(echo) == 1:
            StopTime = time.time()
     
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2 
        return distance
    
    if __name__ == '__main__':
        while True:
            
            if(stopQueue.empty()):
                dist = distance()
                print ("Measured Distance = %.1f cm" % dist)          
                if(dist <= obstacleDist):
                    print("Obstacle detected")
                    objectQueue.put_nowait("obstacle")
                else:
                    pass
                time.sleep(0.5)
            else:
                stopFlag = stopQueue.get_nowait()
                print("queue content: ",stopFlag)
                if(stopFlag == "stop ultrasonic"):
                    print("Stop measurement")
                    GPIO.cleanup()
                    break

if __name__ == '__main__':


    stopQueue = Queue()
    objectQueue = Queue()
    cameraLeftQueue = Queue()
    cameraRightQueue = Queue()
    
    ultrasonic = Process(target=ultrasonic,args=( (stopQueue),(objectQueue) ) )
    ultrasonic.start()
    camera = Process( target=camera, args=( (stopQueue),(objectQueue),(cameraLeftQueue), (cameraRightQueue) ) )
    camera.start()

    while(camera.is_alive()):
        pass
    else:
        nonZeroLeft = cameraLeftQueue.get_nowait()
        nonZeroRight = cameraRightQueue.get_nowait()
                        
        saveOutput = input("Save File? Type 'Y' for yes and 'N' for no \n")
        if(saveOutput == "Y" or saveOutput == "y"):
            
            for counter in range (0, len(nonZeroLeft)):                
                dataLeftX.append(nonZeroLeft[counter][0][0])
                dataLeftY.append(nonZeroLeft[counter][0][1])
                
            for counter in range (0, len(nonZeroRight)):
                dataRightX.append(nonZeroRight[counter][0][0])
                dataRightY.append(nonZeroRight[counter][0][1])

##            print(dataLeftX)
##            print(dataLeftY)
##            print(dataRightX)
##            print(dataRightY)

            timeString = time.strftime("%Y%m%d-%H%M%S")

            with open ('/home/pi/Desktop/FYP/Data/%s.csv' %timeString,'w',newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter = ',')
                writer.writerow(dataLeftX)
                writer.writerow(dataLeftY)
                writer.writerow(dataRightX)
                writer.writerow(dataRightY)
                
            cv2.imwrite('/home/pi/Desktop/FYP/Data/%s.png' %timeString ,edges)
            print("Output is saved")
        else:
            print("Output not saved")
