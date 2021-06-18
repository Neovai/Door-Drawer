#!/usr/bin/env python

#from constants import *
from time import time
import spidev #used for mcp3008
import RPi.GPIO as gpio
import VL53L0X
from stepper_motor import StepperMotor
from drawer_data import DataPoint

#gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins
#
##spi setup for MCP3008's
#spi_lower = spidev.SpiDev()
##spi_lower.open(1, 0) #seperate bus, can be used for multiprocessing
#spi_lower.open(0, 1) #same bus, synchronous
#spi_lower.max_speed_hz = 1000000
#spi_upper = spidev.SpiDev()
#spi_upper.open(0, 0)#bus for mcp3008 in charge of FSR's 8 - 12
#spi_upper.max_speed_hz = 1000000
#
##set pins as output pins
#gpio.setup(reset_pul, gpio.OUT)
#gpio.setup(reset_dir, gpio.OUT)
#gpio.setup(reset_en, gpio.OUT)
#gpio.setup(fric_pul, gpio.OUT)
#gpio.setup(fric_dir, gpio.OUT)
#gpio.setup(fric_en, gpio.OUT)
#
#
##helper function for controlling motors
##direction: 0 = forward, 1 = reverse
##run_time: seconds. Enter 0 for runtime to do one pulse cycle
##motor: 0 = reset motor, 1 = friction motor
#def move(motor, direction, run_time, speed = 0):
#    #reset motor
#    if(motor == 0):
#        pulse_pin = reset_pul
#        dir_pin = reset_dir
#        en_pin = reset_en
#    #friction motor
#    elif(motor == 1):
#        pulse_pin = fric_pul
#        dir_pin = fric_dir
#        en_pin = fric_en
#    else:
#        return -1
#    #print("pulse: {} -- dir: {} -- en: {} -- speed: {}".format(pulse_pin, dir_pin, en_pin, speed))
#    gpio.output(dir_pin, direction)
#    gpio.output(en_pin, gpio.HIGH)
#    timer = time() + run_time
#    while True:
#        gpio.output(pulse_pin, gpio.HIGH)
#        sleep(speed)
#        gpio.output(pulse_pin, gpio.LOW)
#        sleep(speed)
#        if(time() >= timer): #emulates a do-while loop
#            break
#    gpio.output(en_pin, gpio.LOW)
#    return


class Drawer:

  def __init__(self):
    self.tof = VL53L0X.VL53L0X()
    self.spi_lower = spidev.SpiDev()
    #spi_lower.open(1, 0) #seperate bus, can be used for multiprocessing
    self.spi_lower.open(0, 1) #same bus, synchronous
    self.spi_lower.max_speed_hz = 1000000
    self.spi_upper = spidev.SpiDev()
    self.spi_upper.open(0, 0)#bus for mcp3008 in charge of FSR's 8 - 12
    self.spi_upper.max_speed_hz = 1000000

    self.reset_pul = 5 #pin 29
    self.reset_dir = 6 # pin 31 
    self.reset_en = 16  # pin 33, (High to Enable / LOW to Disable)
    self.time_unwind = 2 #in seconds
    self.reset_speed = .000001 # seconds
    self.dis_buffer = 5 #buffer value for resetting drawer (in mm)
    self.fric_pul = 17 #pin 11
    self.fric_dir = 27 # pin 13
    self.fric_en = 22  # pin 15 (High to Enable / LOW to Disable)
    self.fric_steps = .00032 #relation between friction to # of motor steps
    self.fric_speed = .000001 #seconds
    self.fric_min_steps = 2500 #min steps it takes to get brake to touch drawer
    self.base_friction = 0.3 #minimum resistance drawer has (in kg)

    gpio.setmode(gpio.BCM) #sets pin mapping to GPIO pins
    gpio.setup(self.reset_pul, gpio.OUT)
    gpio.setup(self.reset_dir, gpio.OUT)
    gpio.setup(self.reset_en, gpio.OUT)
    gpio.setup(self.fric_pul, gpio.OUT)
    gpio.setup(self.fric_dir, gpio.OUT)
    gpio.setup(self.fric_en, gpio.OUT)
    
    self.reset_motor = StepperMotor(self.reset_pul, self.reset_dir, self.reset_en)
    self.fric_motor = StepperMotor(self.fric_pul, self.fric_dir, self.fric_en)
    self.__trial_data = []
  
  def __set_friction(self):
    self.fric_motor.step(self.__resistance_steps, self.fric_motor.CW)
    gpio.output(self.fric_en, gpio.HIGH) #keep motor resistance on
  
  def __reset_friction(self):
    self.fric_motor.step_to(0)
    
  def __read_handle(self):
    data = [-1] * 14
    #lower ADC
    for chan in range(0,8):
      r = self.spi_lower.xfer2([1, 8 + chan << 4, 0])
      data[chan] = int(((r[1] & 3) << 8) + r[2])
    #spidev automatically switches CS signals
    #upper ADC
    for chan in range(0,4):
      r = self.spi_upper.xfer2([1, 8 + chan << 4, 0])
      data[chan + 8] = int(((r[1] & 3) << 8) + r[2])
    return data
    
#  def __clean_trial(self):
#    print("length of trial_data: {}".format(len(self.__trial_data)))
#    for i in range(0, len(self.__trial_data)):
#      print(i)
#      del self.__trial_data[i]
  
  def start_new_trial(self, resistance, tof_mode = 0):
    self.tof_mode = tof_mode
    self.__resistance_steps = int(((resistance - self.base_friction) / self.fric_steps) + self.fric_min_steps)
    self.tof.start_ranging(self.tof_mode)
    self.start_pos = self.tof.get_distance()
    self.__set_friction()
    #self.__clean_trial() 
    self.__trial_data = [] #not need?
  
  def collect_data(self):
    data_point = DataPoint(self.tof.get_distance() - self.start_pos, self.__read_handle(), time())
    self.__trial_data.append(data_point)
  
  def reset(self):
    self.__reset_friction()
    did_move = False
    end_pos = self.start_pos + self.dis_buffer
    while (True):
      if(self.tof.get_distance() <= end_pos):
        break
      did_move = True
      self.reset_motor.move_for(0.1, self.reset_motor.CCW)
    if(did_move):
      print("undo?")
      self.reset_motor.move_for(self.time_unwind, self.reset_motor.CW)
    self.tof.stop_ranging()
    
  def get_trial_data(self):
    return self.__trial_data
    
  def __del__(self):
    gpio.cleanup()
    #self.__clean_trial()
    del self.__trial_data
    

##returns array of all fsr values (MCP3008)
#def readHandle():
#    data = [-1] * 14
#    #lower ADC
#    for chan in range(0,8):
#        r = spi_lower.xfer2([1, 8 + chan << 4, 0])
#        data[chan] = int(((r[1] & 3) << 8) + r[2])
#    #spidev automatically switches CS signals
#    #upper ADC
#    for chan in range(0,4):
#        r = spi_upper.xfer2([1, 8 + chan << 4, 0])
#        data[chan + 8] = int(((r[1] & 3) << 8) + r[2])
#    return data
#
#def resetDrawer(start_pos, acc_setting, tof):
#    did_move = False
#    tof.start_ranging(acc_setting)
#    print("Resetting Drawer...")
#    while (True):
#        if(tof.get_distance() <= (start_pos + dis_buffer)):
#            break
#        did_move = True
#        move(reset_motor, 1, 0.1, reset_speed)
#    
#    if(did_move):
#        print("Unwinding Motor...")
#        move(reset_motor, 0, time_unwind, reset_speed)
#    tof.stop_ranging()
#    return
#
##works mechanically. Test actual resistance accuracy
#def setFriction(resistance = .3):
#    num_steps = int(((resistance - base_friction) / fric_steps)
#            + fric_min_steps)
#    print(num_steps)
#    for steps in range(1, num_steps):
#        move(fric_motor, 0, 0, fric_speed)
#    gpio.output(fric_en, gpio.HIGH) #keep motor resistance on
#    return num_steps
#
#def resetFriction(num_steps):
#    for steps in range(1, num_steps):
#        move(fric_motor, 1, 0, fric_speed)

