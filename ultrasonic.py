import time
time1 = time.time()
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
US_trigger = 26
US_echo = 19

GPIO.setup(US_trigger, GPIO.OUT)
GPIO.setup(US_echo, GPIO.IN)

def distance():
    # set Trigger to HIGH
    GPIO.output(US_trigger, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(US_trigger, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(US_echo) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(US_echo) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            time.sleep(0.1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
