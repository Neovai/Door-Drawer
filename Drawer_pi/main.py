"""
Start by doing a 1:1 copy of the arduino version.
Afterwards, look into threading w/ multiprocessing.dummy

5/22: move() function is working properly
      TOF is working properly (need to test replication on another pi)
"""
import sys, platform, threading
from time import sleep, time
import spidev
import RPi.GPIO as gpio
import VL53L0X

print("hello")
sleep(1)
print("sleep works on: " + platform.python_version())

gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins


#reset motor settings/pins
reset_motor = 0 #defines reset motor (for use with move() fxn)
reset_pul = 17 #pin 11. 17/27 are the GPIO pin #
reset_dir = 27 # pin 13 
reset_en = 22  # pin 15, (High to Enable / LOW to Disable)
time_unwind = 4 #in seconds
reset_speed = .0000001 #time in between pulses to MC (in seconds). controls speed of motor

#friction motor settings/pins
#use GPIO 23,24,25 (pins 16,18,22) for control pins

#set pins as output pins
gpio.setup(reset_pul, gpio.OUT)
gpio.setup(reset_dir, gpio.OUT)
gpio.setup(reset_en, gpio.OUT)

#function for controlling motors
#direction: 0 = forward, 1 = reverse
<<<<<<< HEAD
#run_time: seconds. Enter 0 for runtime to do one pulse cycle
=======
#run_time: seconds
#motor: 0 = reset motor, 1 = friction motor
>>>>>>> a6b68b341c1170cbcb68543df6e368aa2b712c15
def move(motor, direction, run_time, speed = 0):
    #reset motor
    if(motor == 0):
        pulse_pin = reset_pul
        dir_pin = reset_dir
        en_pin = reset_en
    #friction motor
    else:
        pass #add friction motor here

    gpio.output(dir_pin, direction) #works for now, alternative is gpio.LOW/HIGH
    gpio.output(en_pin, gpio.HIGH)
    timer = time() + run_time
    while True:
        gpio.output(pulse_pin, gpio.HIGH)
        sleep(speed)
        gpio.output(pulse_pin, gpio.LOW)
        sleep(speed)
        if(time() >= timer): #emulates a do-while loop
            break
    gpio.output(en_pin, gpio.LOW)
    return

#test motor function:
<<<<<<< HEAD
for i in range(0,1):
    print("direction 1")
    move(reset_motor, 1, time_unwind, reset_speed)
    sleep(.5)
    print ("direction 0")
    move(reset_motor, 0, time_unwind, reset_speed)
    sleep(.5)
gpio.cleanup()


#TOF testing

sample_data = [0] * 100;

def avg(data):
    return sum(data) / len(data)

# Create a VL53L0X object
tof = VL53L0X.VL53L0X()

# Start ranging
#tof.start_ranging(1) # better acc. mode
#tof.start_ranging(2) # best acc. mode
tof.start_ranging(0) #good acc. mode
#tof.start_ranging(3) #long range mode
#tof.start_ranging(4) # high speed mode

#timing = tof.get_timing()
for i in range(0, len(sample_data)):
    sample_data[i] = tof.get_distance()

print("min range value: %d" % (min(sample_data)))
print("max range value: %d" % (max(sample_data)))
a = avg(sample_data)
print(a)
tof.stop_ranging()

=======
move(reset_motor, 1, time_unwind, reset_speed)
print("ran at speed: %s" % reset_speed)
>>>>>>> a6b68b341c1170cbcb68543df6e368aa2b712c15
