"""
Start by doing a 1:1 copy of the arduino version.
Afterwards, look into threading w/ multiprocessing.dummy

5/22: move() function is working properly
      TOF is working properly (need to test replication on another pi)

5/24: can read block from ADS1115. readADC() needs to be tested. Need to test how many SPI bus's are available
      (might need to use one bus and SS pins to enable each mcp3008)
      second I2C port does NOT work

6/10: reset drawer works with i2c ADC and TOF. setFriction and resetFricion function properly
"""
import sys, platform, threading
from time import sleep, time
#import spidev #used for mcp3008
#from smbus2 import SMBus #used for i2c communication with ADS1115
#import RPi.GPIO as gpio
import VL53L0X
from helpers.drawer_functions import *
#from helpers.drawer_functions import *

print("python version: " + platform.python_version())

#TOF object/settings
tof = VL53L0X.VL53L0X()
"""
gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins

#spi setup for MCP3008's
spi_lower = spidev.SpiDev()
spi_lower.open(1, 0) #bus for mcp3008 in charge of FSR's 1 - 7
spi_lower.max_speed_hz = 1000000
spi_upper = spidev.SpiDev() 
spi_upper.open(0, 0)#bus for mcp3008 in charge of FSR's 8 - 12
spi_upper.max_speed_hz = 1000000


#reset motor settings/pins
reset_motor = 0 #defines reset motor (for use with move() fxn)
reset_pul = 5 #pin 29
reset_dir = 6 # pin 31 
reset_en = 16  # pin 33, (High to Enable / LOW to Disable)
time_unwind = 2 #in seconds
reset_speed = .000001 #time in between pulses to MC (in seconds). controls speed of motor
dis_buffer = 5 #buffer value for resetting drawer (in mm)

#friction motor settings/pins
fric_motor = 1 #defines reset motor (for use with move() fxn)
fric_pul = 17 #pin 11
fric_dir = 27 # pin 13
fric_en = 22  # pin 15 (High to Enable / LOW to Disable)
fric_steps = .00032 #relation between friction to # of motor steps
fric_speed = .000001 #time in between pulses to MC (in seconds). controls speed of motor
fric_min_steps = 2500 #min steps it takes to get brake to touch drawer fin
base_friction = 0.3 #minimum resistance drawer has (in kg)

#set pins as output pins
gpio.setup(reset_pul, gpio.OUT)
gpio.setup(reset_dir, gpio.OUT)
gpio.setup(reset_en, gpio.OUT)
gpio.setup(fric_pul, gpio.OUT)
gpio.setup(fric_dir, gpio.OUT)
gpio.setup(fric_en, gpio.OUT)

#function for controlling motors
#direction: 0 = forward, 1 = reverse
#run_time: seconds. Enter 0 for runtime to do one pulse cycle
#motor: 0 = reset motor, 1 = friction motor
def move(motor, direction, run_time, speed = 0):
    #reset motor
    if(motor == 0):
        pulse_pin = reset_pul
        dir_pin = reset_dir
        en_pin = reset_en
    #friction motor
    elif(motor == 1):
        pulse_pin = fric_pul
        dir_pin = fric_dir
        en_pin = fric_en
    else:
        return -1
    #print("pulse: {} -- dir: {} -- en: {} -- speed: {}".format(pulse_pin, dir_pin, en_pin, speed))
    gpio.output(dir_pin, direction)
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

#NEEDS TESTING
#returns array of all fsr values (MCP3008)
def readHandle():
    data = [-1] * 14 #last two are placeholders for drawer
    #lower ADC
    for chan in range(0,8):
        r = spi_lower.xfer2([1, 8 + chan << 4, 0])
        data[chan] = ((r[1] & 3) << 8) + r[2]
    #upper ADC
    for chan in range(0,4):
        r = spi_upper.xfer2([1, 8 + chan << 4, 0])
        data[chan + 8] = ((r[1] & 3) << 8) + r[2]
    return data

def resetDrawer(start_pos, acc_setting):
    did_move = False
    tof.start_ranging(acc_setting)
    print("Resetting Drawer...")
    while (True):
        if(tof.get_distance() <= (start_pos + dis_buffer)):
            break
        did_move = True
        move(reset_motor, 1, 0.1, reset_speed)
    
    if(did_move):
        print("Unwinding Motor...")
        move(reset_motor, 0, time_unwind, reset_speed)
    
    tof.stop_ranging()
    return

#works mechanically. Test actual resistance accuracy
def setFriction(resistance = .3):
    num_steps = int(((resistance - base_friction) / fric_steps)
            + fric_min_steps)
    print(num_steps)
    for steps in range(1, num_steps):
        move(fric_motor, 0, 0, fric_speed)
    gpio.output(fric_en, gpio.HIGH) #keep motor resistance on
    return num_steps

def resetFriction(num_steps):
    for steps in range(1, num_steps):
        move(fric_motor, 1, 0, fric_speed)

#test motor function:
#try: 
#    for i in range(0,1):
#        print("direction 1")
#        move(fric_motor, 1, 1, fric_speed)
#        sleep(1)
#        print ("direction 0")
#        move(fric_motor, 0, 1, fric_speed)
#        sleep(1)
#    for i in range(0,1):
#        print("direction 1")
#        move(reset_motor, 1, time_unwind, reset_speed)
#        sleep(1)
#        print ("direction 0")
#        move(reset_motor, 0, time_unwind, reset_speed)
#        sleep(1)
#except KeyboardInterrupt:
#    pass


#TOF testing
#sample_data = [0] * 100;

#def avg(data):
#    return sum(data) / len(data)

# Create a VL53L0X object
#tof = VL53L0X.VL53L0X()

# Start ranging
#tof.start_ranging(1) # better acc. mode
#tof.start_ranging(2) # best acc. mode
#tof.start_ranging(0) #good acc. mode
#tof.start_ranging(3) #long range mode
#tof.start_ranging(4) # high speed mode

#for i in range(0, len(sample_data)):
#    sample_data[i] = tof.get_distance()

#print("min range value: %d" % (min(sample_data)))
#print("max range value: %d" % (max(sample_data)))
#a = avg(sample_data)
#print(a)
#tof.stop_ranging()

#ADC (ADS1115) testing
def pseudoHandle():
    #reads 4 bytes.
    with SMBus(2) as bus: #opens bus 2
        bus.pec = 1 #enables error checking for packet
        data = [-1] * 12
        for i in range(0, 12):
            fsr = bus.read_i2c_block_data(0x48, 0, 1) #address 0x48, offset 0, 1 byte
            data[i] = fsr[0]
        #print(data)
    #automatically closes smbus
    return data
"""
def main():
    while True:
        trial_time = int(raw_input("Trial Time (seconds, -1 to quit): "))
        if(trial_time == -1):
            break
        tof_mode = int(raw_input("TOF mode (0 - 4): "))
        resistance = float(raw_input("Friction Resistance (kg): "))
        fric_num_steps = setFriction(resistance)
        timer = time() + trial_time
        tof.start_ranging(tof_mode)
        start_pos = tof.get_distance() #gets initial distance of drawer. Used for reset
        while(time() < timer):
            #collect data
            distance = tof.get_distance() - start_pos #tof data point
            handle = pseudoHandle() #fsr's data point
            print("{} --- {} --- {}".format(distance, handle, time()))
        #reset drawer
        resetFriction(fric_num_steps)
        tof.stop_ranging()
        resetDrawer(start_pos, tof_mode, tof)
    #cleanup GPIO pins
    gpio.cleanup()
    return

if __name__ == "__main__":
    main()
