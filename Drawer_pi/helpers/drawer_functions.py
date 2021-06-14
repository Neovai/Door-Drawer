from constants import *
from time import sleep, time
import spidev #used for mcp3008
from smbus2 import SMBus #used for i2c communication with ADS1115
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins

#spi setup for MCP3008's
spi_lower = spidev.SpiDev()
spi_lower.open(1, 0) #bus for mcp3008 in charge of FSR's 1 - 7
spi_lower.max_speed_hz = 1000000
spi_upper = spidev.SpiDev() 
spi_upper.open(0, 0)#bus for mcp3008 in charge of FSR's 8 - 12
spi_upper.max_speed_hz = 1000000

#set pins as output pins
gpio.setup(reset_pul, gpio.OUT)
gpio.setup(reset_dir, gpio.OUT)
gpio.setup(reset_en, gpio.OUT)
gpio.setup(fric_pul, gpio.OUT)
gpio.setup(fric_dir, gpio.OUT)
gpio.setup(fric_en, gpio.OUT)


#helper function for controlling motors
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

def resetDrawer(start_pos, acc_setting, tof):
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
