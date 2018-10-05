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

        # main logic variables
        leftX1 = 0
        leftY1 = 0
        leftX2 = 319
        leftY2 = 479

        totalLeft = 0
        prevLeftY = 0
        currentLeftY = 0
        diffLeftY = 0
        countLeft = 0
        indexY = 0

        currentLeftX1 = 0
        currentLeftX2 = 0
        diffLeftX1 = 0
        diffLeftX2 = 0
        criticalLeftX1 = -1
        criticalLeftX2 = -1

        # Flags
        criticalLeftY = -1


        rightX1 = 320
        rightY1 = 0
        rightX2 = 639
        rightY2 = 479

        totalRight = 0

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

        
            # image array, try do processing here?
            image = frame.array

            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
##            cannyMin = cv2.getTrackbarPos('Canny Min','window')
##            cannyMax = cv2.getTrackbarPos('Canny Max','window')
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
                # retrieve critical Y value and break loop
                for counter in range(0, len(nonZeroLeft)):
                    if(criticalLeftY != -1):
                        break
                    if(counter == 0):
                        prevLeftY = nonZeroLeft[counter][0][1]
                    else:
                        currentLeftY = nonZeroLeft[counter][0][1]
                        diffLeftY = currentLeftY - prevLeftY
                        if(diffLeftY == 0):
                            countLeft = 0
                        else:
                            if(countLeft == 1):
                                print("critical Y value is: ",prevLeftY)
                                criticalLeftX1 = nonZeroLeft[counter][0][0]
                                criticalLeftX2 = nonZeroLeft[counter][0][0]
                                print("critical X value is: ",criticalLeftX1)
                                criticalLeftY = 0
                                indexY = counter
                                break
                            else:
                                prevLeftY = currentLeftY
                                countLeft += 1

                # only add if X value is within critical range (first half range)
                print(indexY)
                for counter in range(indexY,-1,-1):
                    if(criticalLeftY == -1):
                        break
                    else:
                        currentLeftX1 = nonZeroLeft[counter][0][0]
                        diffLeftX1 = currentLeftX1 - criticalLeftX1
            ##            print("diff: ",diffLeftX)
            ##            print("current: ",currentLeftX)
            ##            print("critical: ",criticalLeftX)
                        if(diffLeftX1 >= -3 and diffLeftX1 <= 3):
                            totalLeft += currentLeftX1
                            criticalLeftX1 = currentLeftX1
            ##                print("add X1")


                for counter in range(indexY+1,len(nonZeroLeft)):
                    if(criticalLeftY == -1):
                        break
                    else:
                        currentLeftX2 = nonZeroLeft[counter][0][0]
                        diffLeftX2 = currentLeftX2 - criticalLeftX2
                        if(diffLeftX2 >= -3 and diffLeftX2 <= 3):
                            totalLeft += currentLeftX2
                            criticalLeftX2 = currentLeftX2
            ##                print("add X2")
            ##                
            ##    print("totalLeftX2: ", totalLeft)

                print("total Left: ",totalLeft)
                criticalLeftY = -1
                print("left: ",leftX2 - (totalLeft/len(nonZeroLeft)))
                totalLeft = 0
                        
            

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

            if key & 0xFF == ord("t"):
                varLeft += 0.1
                print("left: " + "%.1f" %varLeft)
                print("right: " + "%.1f" %varRight)
                
            if key & 0xFF == ord("g"):
                varLeft -= 0.1
                print("left: " + "%.1f" %varLeft)
                print("right: " + "%.1f" %varRight)
                
            if key & 0xFF == ord("y"):
                varRight += 0.1
                print("left: " + "%.1f" %varLeft)
                print("right: " + "%.1f" %varRight)
                
            if key & 0xFF == ord("h"):
                varRight -= 0.1
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
                nonZeroLeft = cv2.findNonZero(leftMask)
                nonZeroRight = cv2.findNonZero(rightMask)
                
                stopQueue.put_nowait("stop ultrasonic")
                cameraLeftQueue.put_nowait(nonZeroLeft)
                cameraRightQueue.put_nowait(nonZeroRight)
                
                break


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
