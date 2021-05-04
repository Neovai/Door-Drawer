"""
Start by doing a 1:1 copy of the arduino version.
Afterwards, look into threading w/ multiprocessing.dummy
"""
import time, sys, platform, threading
import RPi.GPIO as gpio
print("hello")
time.sleep(1)
print("sleep works on: " + platform.python_version())

gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins


#reset motor settings/pins
reset_motor = 0 #defines reset motor (for use with move() fxn)
reset_pul = 17 #pin 11. 17/27 are the GPIO pin #
reset_dir = 27 # pin 13 
time_unwind = 4000 #in ms?? - maybe
reset_speed = .0000001 #time in between pulses to MC (in seconds). controls speed of motor

#set pins as output pins
gpio.setup(pul_reset, gpio.OUT)
gpio.setup(pul_dir, gpio.OUT)

#function for controlling motors
#direction: 0 = forward, 1 = reverse
#time: ms??? - maybe
def move(motor, speed, time, direction = 0):
    #reset motor
    if(motor == 0):
        pulse_pin = reset_pul
        dir_pin = reset_dir
    #friction motor
    else:
        pass #add friction motor here

    gpio.output(dir_pin, direction) #might have to use gpio.LOW
    for t in range(time):
        gpio.output(pulse_pin, gpio.HIGH)
        time.sleep(speed)
        gpio.output(pulse_pin, gpio.LOW)
        time.sleep(speed)
    return

#test motor function:
move(reset_motor, reset_speed, time_unwind, 1)
