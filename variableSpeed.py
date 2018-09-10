import time
time1 = time.time()
import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO

def regionOfInterest(image, vertices):
    #define blank matrix matching image height & width
    mask = np.zeros_like(image)
    #retrieve number of color channels of image
##    channel_count = image.shape[2]
    #create a match color with same color channel counts
##    match_mask_color = (255,) * channel_count
    match_mask_color = 255
    #fill inside the polygon
    cv2.fillPoly (mask,vertices,match_mask_color)
    #return image only where mask pixel match
    masked_image = cv2.bitwise_and (image, mask)
    return masked_image

def colorOfInterest(image,lower_col,upper_col):
    image = cv2.GaussianBlur(image,(5,5),0)
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(image,image, mask = mask)
    edges = cv2.Canny(res, 300, 500)
    return edges

if __name__ == '__main__':

    #Motor driver pins
    PWMA = 17
    AIN1 = 22
    AIN2 = 27
    PWMB = 13
    BIN1 = 5
    BIN2 = 6

    #default motor speed
    varLeft = 40
    varRight = 40

    GPIO.setwarnings(False) # no gpio wanrings
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

    cameraHeight = 480
    cameraWidth = 640

    # colour settings
    blue = (0,0,0)
    # cardboard color
    lower_red = np.array([130,60,60])
    upper_red = np.array([170,255,255])
    #coordinate settings
    middleBottom = (int(cameraWidth/2),int(cameraHeight))
    middleTop = (int(cameraWidth/2),int(cameraHeight-cameraHeight))
    print(middleBottom)
    print(middleTop)

    roi_vertices = [(0,cameraHeight),(int(cameraWidth/2),int(cameraHeight-cameraHeight)),(cameraWidth,cameraHeight)]

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

        output = image.copy()
        
        image = cv2.line(image, middleBottom, middleTop, blue, 5)

        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        canny_image = cv2.Canny(gray_image, 300, 500)
        
        cropImage = regionOfInterest(canny_image, np.array([roi_vertices],np.int32),)
##        detectColor = colorOfInterest(cropImage, lower_red, upper_red)
##        cv2.addWeighted(detectColor, 0.5, image, 0.5 , 0.0, output)
        
        # show frame
        cv2.imshow("Image", image)
        cv2.imshow("Crop", cropImage)
##        cv2.imshow("Color", detectColor)
                
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
            break
            
    time2 = time.time()
    print ('Elapsed time : ', time2-time1,'secs')
    GPIO.cleanup() #important to have to reset the GPIOs
