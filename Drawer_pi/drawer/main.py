#!/usr/bin/env python
#
# Author: Ryan Roberts
#
# Testing code for Drawer

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
