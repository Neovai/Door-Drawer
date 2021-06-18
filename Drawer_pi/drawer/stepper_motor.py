#!/usr/bin/env python
from time import time, sleep
import RPi.GPIO as gpio

class StepperMotor:

  CCW = 1
  CW = 0

  def __init__(self, pulse_pin, dir_pin, en_pin, default_speed = None):
    if(default_speed == None):
      default_speed = .000001
    try:
      self.pulse_pin = int(pulse_pin)
      self.dir_pin = int(dir_pin)
      self.en_pin = int(en_pin)
    except ValueError:
      print("Invalid pin assignments")
    try:
      self.default_speed = float(default_speed)
    except ValueError:
      print("Invalid default speed")
    self.__current_steps = 0
  
  def move_for(self, run_time, direction, speed = None):
    if(speed == None):
      speed = self.default_speed
    gpio.output(self.dir_pin, direction)
    gpio.output(self.en_pin, gpio.HIGH)
    inc = 0
    if(direction==self.CW):
      inc = 1
    elif(direction==self.CCW):
      inc = -1
    else:
      print("Invalid direction")
      return -1
    timer = time() + run_time
    while(time() <= timer):
      gpio.output(self.pulse_pin, gpio.HIGH)
      sleep(speed)
      gpio.output(self.pulse_pin, gpio.LOW)
      sleep(speed)
      self.__current_steps += inc
    gpio.output(self.en_pin, gpio.LOW)
  
  def step(self, num_steps, direction, speed = None):
    if(speed == None):
      speed = self.default_speed
    gpio.output(self.dir_pin, direction)
    gpio.output(self.en_pin, gpio.HIGH)
    if(direction==self.CW):
      self.__current_steps += num_steps
    elif(direction==self.CCW):
      self.__current_steps -= num_steps
    else:
      print("Invalid direction")
      return -1
    for steps in range(num_steps):
      gpio.output(self.pulse_pin, gpio.HIGH)
      sleep(speed)
      gpio.output(self.pulse_pin, gpio.LOW)
      sleep(speed)
    gpio.output(self.en_pin, gpio.LOW)
    
  def step_to(self, step_target, speed = None):
    if(speed == None):
      speed = self.default_speed
    try:
      num_steps = int(step_target) - self.__current_steps
      if(num_steps >= 0):
        self.step(abs(num_steps), self.CW, speed)
      else:
        self.step(abs(num_steps), self.CCW, speed)
      self.__current_steps = step_target
    except ValueError:
      print("Invalid step target")
  
  def get_current_steps(self):
    return self.__current_steps
    