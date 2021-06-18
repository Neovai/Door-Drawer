#!/usr/bin/env python

##reset motor settings/pins
#reset_motor = 0 #defines reset motor (for use with move() fxn)
#reset_pul = 5 #pin 29
#reset_dir = 6 # pin 31 
#reset_en = 16  # pin 33, (High to Enable / LOW to Disable)
#time_unwind = 2 #in seconds
#reset_speed = .000001 #time in between pulses to MC (in seconds). controls speed of motor
#dis_buffer = 5 #buffer value for resetting drawer (in mm)
#
##friction motor settings/pins
#fric_motor = 1 #defines friction motor (for use with move() fxn)
#fric_pul = 17 #pin 11
#fric_dir = 27 # pin 13
#fric_en = 22  # pin 15 (High to Enable / LOW to Disable)
#fric_steps = .00032 #relation between friction to # of motor steps
#fric_speed = .000001 #time in between pulses to MC (in seconds). controls speed of motor
#fric_min_steps = 2500 #min steps it takes to get brake to touch drawer fin
#base_friction = 0.3 #minimum resistance drawer has (in kg)
