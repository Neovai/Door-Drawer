#!/usr/bin/env python
from time import time, sleep
import RPi.GPIO as gpio

#TODO:
# add attribute that asks what kind of stepping there is to record actual step counts
# add set_zero function that sets current_steps to 0
# add raise errors instead of print,return. Add more as well

class StepperMotor:
  """
  A class used to run a stepper motor with a motor controller
  on a Raspberry Pi
  
  ...
  
  Attributes
  ----------
  CCW : int
    describes the counterclockwise direction of stepper motor (default 1)
  CW : int
    describes the clockwise direction of stepper motor (default 0)
  pulse_pin : int
    GPIO pin number for pulse pin of stepper motor controller
  dir_pin : int
    GPIO pin number for direction pin of stepper motor controller
  en_pin : int
    GPIO pin number for enable pin of stepper motor controller
  default_speed : float
    delay between pulses in seconds / 2 (default .000001)
  current_steps : int
    step count of stepper motor relative to its zero position
  
  Methods
  -------
  move_for(run_time, direction, speed = None):
    moves motor in a single direction for a given time
  step(num_steps, direction, speed = None):
    steps motor in a single direction for a given amount of steps
  step_to(step_target, speed = None):
    steps motor to a specific step relative to its zero positon
  get_current_steps():
    returns current step position of motor
  """
  
  CCW = 1
  CW = 0

  def __init__(self, pulse_pin, dir_pin, en_pin, default_speed = None):
    """
    Constructor
    
    Parameters
    ----------
    pulse_pin : int
      GPIO pin number for pulse pin of stepper motor controller
    dir_pin : int
      GPIO pin number for direction pin of stepper motor controller
    en_pin : int
      GPIO pin number for enable pin of stepper motor controller
    default_speed : float, optional
      delay between pulses in seconds / 2 (default .000001)
    """
    
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
    """
    Moves motor in a single direction for a given time.
    Note: number of steps made by motor may vary using this method.
    Do not use for precise movements
    
    Parameters
    ----------
    run_time : float
      time in seconds for motor to run
    direction : int
      direction for motor to move in. Highly suggest using CW and CCW
      class variables
    speed : float, optional
      delay between pulses in seconds / 2 (default default_speed)
      
    Returns
    -------
    None
    """
    
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
    """
    Steps motor in a single direction for a given amount of steps
    
    Parameters
    ----------
    num_steps : int
      number of steps to move motor
    direction : int
      direction for motor to move in. Highly suggest using CW and CCW
      class variables
    speed : float, optional
      delay between pulses in seconds / 2 (default default_speed)
      
    Returns
    -------
    None
    """
    
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
    """
    Steps motor to a specific step relative to its zero positon
    
    Parameters
    ----------
    step_target : int
      target step position to move motor to
    speed : float, optional
      delay between pulses in seconds / 2 (default default_speed)
      
    Raises
    ------
    ADD HERE
      
    Returns
    -------
    None
    """
    
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
    """
    Returns current step position of motor.
    Negative steps = CCW direction
    Positive steps = CW direction
    
    Parameters
    ----------
    None
      
    Returns
    -------
    int
    """
    
    return self.__current_steps
    
