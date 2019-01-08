import RPi.GPIO as GPIO


settings = {
    
"PWMA" : 17,
"AIN1" : 22,
"AIN2" : 27,
"PWMB" : 13,
"BIN1" : 5,
"BIN2" : 6,
"STNBY" : 18,
"PWMA_PW" : 1,
"PWMB_PW" : 1,
"cannyMin" : 80,
"cannyMax" : 100,
"minLineLength" : 100,
"maxLineGap" : 100
}

def config ():
    return settings

if __name__ == '__main__':
    print("PWMA pin: ", settings["PWMA"])
    print("AIN1 pin: ", settings["AIN1"])
    print("AIN2 pin: ", settings["AIN2"])
    print("PWMB pin: ", settings["PWMB"])
    print("BIN1 pin: ", settings["BIN1"])
    print("BIN2 pin: ", settings["BIN2"])
    print("STNBY pin: ", settings["STNBY"])
    print("PWMB pulse width: ", settings["PWMA_PW"])
    print("PWMB pulse width: ", settings["PWMB_PW"])
