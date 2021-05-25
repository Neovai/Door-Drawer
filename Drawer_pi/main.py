"""
Start by doing a 1:1 copy of the arduino version.
Afterwards, look into threading w/ multiprocessing.dummy

5/22: move() function is working properly
      TOF is working properly (need to test replication on another pi)

5/24: can read block from ADS1115. readADC() needs to be tested. Need to test how many SPI bus's are available
      (might need to use one bus and SS pins to enable each mcp3008)
      second I2C port does NOT work
"""
import sys, platform, threading
from time import sleep, time
import spidev #used for mcp3008
from smbus2 import SMBus #used for i2c communication with ADS1115
import RPi.GPIO as gpio
import VL53L0X

print("sleep works on: " + platform.python_version())

gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins

#spi setup for MCP3008's
spi_lower = spidev.SpiDev()
#(1,0) throws an error, SPI bus not activated? need to use only one bus?
#spi_lower.open(1, 0) #bus for mcp3008 in charge of FSR's 1 - 7
#spi_lower.max_speed_hz = 1000000
spi_upper = spidev.SpiDev() 
spi_upper.open(0, 0)#bus for mcp3008 in charge of FSR's 8 - 12
spi_upper.max_speed_hz = 1000000

#TOF object/settings
tof = VL53L0X.VL53L0X()
acc_setting = 3 #good accuracy

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
#run_time: seconds. Enter 0 for runtime to do one pulse cycle
#motor: 0 = reset motor, 1 = friction motor
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

#NEEDS TESTING
#returns single channel value for an ADC
# @param chan = channel number on ADC (0 - 7)
# @param dev = spiDev() object
def readADC(chan, dev):
    #only 8 channels on MCP3008
    if(chan > 7 or chan < 0):
        return -1
    r = dev.xfer2([1, 8 + chan << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

#NEEDS TESTING
def resetDrawer(start_pos):
    bool did_move = False
    tof.start_ranging(acc_setting)
    while (True):
        if(tof.get_distance() <= start_pos):
            break
        did_move = True
        move(reset_motor, 1, 0, reset_speed)
    
    if(did_move):
        move(reset_motor, 0, time_unwind, reset_speed)
    
    tof.stop_ranging()
    return

#test motor function:
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
#tof.start_ranging(0) #good acc. mode
tof.start_ranging(3) #long range mode
#tof.start_ranging(4) # high speed mode

for i in range(0, len(sample_data)):
    sample_data[i] = tof.get_distance()

print("min range value: %d" % (min(sample_data)))
print("max range value: %d" % (max(sample_data)))
a = avg(sample_data)
print(a)
tof.stop_ranging()

#ADC (ADS1115) testing
#reads 4 bytes. Works? -> returns array of values of 0/255
#with SMBus(1) as bus: #opens bus 1
    #bus.pec = 1 #enables error checking for packet
    #block = bus.read_i2c_block_data(0x48, 0, 4) #address 0x48, offset 0, 4 bytes
    #print(block)
#automatically closes smbus
