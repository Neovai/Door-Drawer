<p>The Drawer_data_collection and door_data_collection was used to collect data from the Door and Drawer with a python script (not main code). 
The Door_code and Drawer_code have UI's that use the Arduino IDE and are only for tetsing the Door/Drawer through the arduino.
Door_ros and Drawer_ros are the final versions of the code that is used for interfacing with ros.</p>

<h3>Drawer_pi Firmware Changes:</h3>
<p>add to syscfg.txt file in /boot/firmware directory: (use nano)</p>
<ul>
  <li>dtoverlay=i2c0</li>
  </li>dtoverlay=spi1-1cs</li>
  </ul>
<p>1cs refers to number of chip select pins activated for that bus (can be 2 or 3)</p>
