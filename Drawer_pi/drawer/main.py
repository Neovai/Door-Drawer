#!/usr/bin/env python
"""
Start by doing a 1:1 copy of the arduino version.
Afterwards, look into threading w/ multiprocessing.dummy

5/22: move() function is working properly
      TOF is working properly (need to test replication on another pi)

5/24: can read block from ADS1115. readADC() needs to be tested. Need to test how many SPI bus's are available
      (might need to use one bus and SS pins to enable each mcp3008)
      second I2C port does NOT work

6/10: reset drawer works with i2c ADC and TOF. setFriction and resetFricion function properly

6/14: updated code to best practices
"""
from drawer import Drawer
from time import time

if __name__ == "__main__":
  drawer = Drawer()
  while True:
    #testing UI
    trial_time = int(raw_input("Trial Time (seconds, -1 to quit): "))
    if(trial_time == -1):
      break
    tof_mode = int(raw_input("TOF mode (0 - 4): "))
    resistance = float(raw_input("Friction Resistance (kg): "))
    drawer.start_new_trial(resistance, tof_mode)
    timer = time() + trial_time
    while(time() <= timer):
      drawer.collect_data()
    drawer.reset()
    trial_data = drawer.get_trial_data()
    for i in range(0, len(trial_data)):
      print(trial_data[i].handle_data)
    print("Length of trial: {}".format(len(trial_data)))
  del drawer

#import sys, platform, threading
#from time import time
#import VL53L0X
#from helpers.drawer_functions import *
#
#print("python version: " + platform.python_version())
#
##TOF object
#tof = VL53L0X.VL53L0X()
#
#def main():
#    while True:
#        trial_time = int(raw_input("Trial Time (seconds, -1 to quit): "))
#        if(trial_time == -1):
#            break
#        tof_mode = int(raw_input("TOF mode (0 - 4): "))
#        resistance = float(raw_input("Friction Resistance (kg): "))
#        fric_num_steps = setFriction(resistance)
#        timer = time() + trial_time
#        tof.start_ranging(tof_mode)
#        start_pos = tof.get_distance() #gets initial distance of drawer. Used for reset
#        try:
#            while(time() < timer):
#                #collect data
#                distance = tof.get_distance() - start_pos #tof data point
#                handle = readHandle()#pseudoHandle() #fsr's data point
#                print("{} --- {} --- {}".format(distance, handle, time()))
#        except KeyboardInterrupt:
#            pass
#        #reset drawer
#        resetFriction(fric_num_steps)
#        tof.stop_ranging()
#        resetDrawer(start_pos, tof_mode, tof)
#    #cleanup GPIO pins
#    gpio.cleanup()
#    return
#
#if __name__ == "__main__":
#    main()
