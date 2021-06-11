<p>The Drawer_data_collection and door_data_collection was used to collect data from the Door and Drawer with a python script (not main code). 
The Door_code and Drawer_code have UI's that use the Arduino IDE and are only for tetsing the Door/Drawer through the arduino.
Door_ros and Drawer_ros are the final versions of the code that is used for interfacing with ros.</p>

<h3>Drawer_pi Firmware Changes:</h3>
<p>add to <b>syscfg.txt</b> file in <b>/boot/firmware</b> directory: <i>(use nano)</i></p>
<ul>
  <li>dtoverlay=i2c-gpio,bus=2,i2c_gpio_sda=23,i2c_gpio_scl=24 (GPIO pins 23,24. can be switched with any pin #'s)</li>
  <li>dtoverlay=spi1-1cs  (1cs refers to number of chip select pins activated for that bus. Can be 2 or 3)</li>
  </ul>
<p>
- be sure to restart pi after saving changes
</p>
