// This script runs the door. The data that it prints out is sensor 1,2,3..., 16 (even though the knob
// only has 10 and the handle 12. Then the FSR 1,2,3,4 on the back of the handle mount.

// heavily modified by: Ryan Roberts

#include "math.h" //Includes math library
#include <Adafruit_MCP3008.h> //Includes library for SPI communications
#include "Adafruit_VL53L0X.h" //library for time of fligh sensor (tof)

//define pins for motor controller
#define enable_motor_channel 46
#define motor_channel1  48
#define motor_channel2  42

// define pins for relay/electromagnet
#define relay25 35
#define relay35 33
#define relay45 44

// define pins for fsr's on handle
#define pot A0
#define fsr1 A1
#define fsr2 A2
#define fsr3 A3
#define fsr4 A4

// Initialize the SPI devices
Adafruit_MCP3008 adc1; //SPI 1
Adafruit_MCP3008 adc2; //SPI 2

//tof sensor
Adafruit_VL53L0X tof = Adafruit_VL53L0X();
float door_angle;

// Initialize user input variables
float magnet_input; //controls wich magnets get turned on for variable resistance on opening the door
float time_input; //controls how long until the door resets itself
float trial_input; //controls how many times user wants to run a test, doesn't need to be used

char junk = ' ';
unsigned long time;
unsigned long stoptime;

//declare motor variable for time to unwind
const int time_unwind = 4500; // in ms

void setup() {
  // Initialize the Serial monitor
  Serial.begin(115200);

  // wait until serial port opens for native USB devices
  while (! Serial) {
    delay(1);
  }

  //if time of flight sensor is not booted correctly, we don't want to run the test on the door
  if (!tof.begin()) {
    Serial.println(F("Failed to boot VL53L0X"));
    while (1);
  }

  // Begins the SPI devices and declares the pins in order of (CLK, MOSI, MISO, CS)
  adc1.begin(52, 51, 50, 53);
  adc2.begin(9, 11, 10, 12);

  // initialize motor pins as outputs
  pinMode(motor_channel1, OUTPUT);
  pinMode(motor_channel2, OUTPUT);
  pinMode(enable_motor_channel, OUTPUT);

  // Initializes electromagnet relay pins as outputs
  pinMode(relay25, OUTPUT);
  pinMode(relay35, OUTPUT);
  pinMode(relay45, OUTPUT);

  // Intialize to turn all the electromagnets off
  digitalWrite(relay25, LOW);
  digitalWrite(relay35, LOW);
  digitalWrite(relay45, LOW);
}

void loop() {
  // Temporary ui for testing the door
 /* Serial.print("Enter desired force rating on a scale of 0 to 7: ");
  while (Serial.available() == 0); {
    magnet_input = Serial.parseFloat();
    Serial.print(magnet_input, 0);
    Serial.print("\n");
    while (Serial.available() > 0) {
      junk = Serial.read();
    }
  }

  Serial.print("Enter How long you would like to run each test (in seconds): ");
  while (Serial.available() == 0); {
    time_input = Serial.parseFloat();
    Serial.print(time_input, 0);
    Serial.print("\n");
    while (Serial.available() > 0) {
      junk = Serial.read();
    }
  }

  Serial.print("Enter How many tests you would like to run: ");
  while (Serial.available() == 0); {
    trial_input = Serial.parseFloat();
    Serial.print(trial_input, 0);
    Serial.print("\n");
    while (Serial.available() > 0) {
      junk = Serial.read();
    }
  }*/
  
 /* for (int i = 1; i <= trial_input; i++) { // runs number of trials
    Serial.print("------- trial ");
    Serial.print(i);
    Serial.print(" -------");
    Serial.print("\n"); */
    Enable_Relays(magnet_input); // changes electromagnets based on input
    time = millis();
    stoptime = time + (time_input * 1000); // converts time_input to seconds

    while (time < stoptime) {
      for (int chan = 0; chan < 8; chan++) {
        Serial.print(adc1.readADC(chan));
        Serial.print("\t");
        Serial.print(adc2.readADC(chan));
        Serial.print("\t");
      }
      Serial.print(analogRead(fsr1));
      Serial.print("\t");
      Serial.print(analogRead(fsr2));
      Serial.print("\t");
      Serial.print(analogRead(fsr3));
      Serial.print("\t");
      Serial.print(analogRead(fsr4));
      Serial.print("\t");
      Serial.print("[");
      Serial.print(time);
      Serial.println("]");

      VL53L0X_RangingMeasurementData_t measure; //value from tof sensor. pointer
      tof.rangingTest(&measure, false);
      if (measure.RangeStatus != 4) {  // phase failures have incorrect data
        door_angle = calc_degree(measure.RangeMilliMeter);
        Serial.print("Angle of Door (deg): "); Serial.print(door_angle); Serial.print(" ");
        //Serial.print("Distance (mm): "); Serial.println(measure.RangeMilliMeter); //prints raw value of tof sensor, used for testing
      }
      
      //if door is opened more than 15 degrees, turn off electromagnets
      //helps keep the electromagnets from overheating
      if(door_angle > 15) 
        Enable_Relays(0);
      else
        Enable_Relays(magnet_input);
      
      delay(50);
      time = millis();
    }
    Reset_Door(); // automatically close door
  //}
}

void Reset_Door() {
  Enable_Relays(0); // turns off magnets; makes motor faster
  while (true) { // door is open more than 2 degrees
    VL53L0X_RangingMeasurementData_t measure; //value from tof sensor
    tof.rangingTest(&measure, false);
    door_angle = calc_degree(measure.RangeMilliMeter);
    digitalWrite(enable_motor_channel, HIGH); //turns motor on
    digitalWrite(motor_channel1, HIGH);// turns motor
    digitalWrite(motor_channel2, LOW); // clockwise
    if (door_angle < 2)
      break;
    delay(100);
  }
  digitalWrite(motor_channel1, LOW); // turns motor
  digitalWrite(motor_channel2, HIGH);// counter clockwise
  delay(time_unwind); //run for certain amount of time
  digitalWrite(enable_motor_channel, LOW); // turns motor off
}

void Enable_Relays(int user_in) {
  if (user_in == 0) {
    digitalWrite(relay25, LOW);
    digitalWrite(relay35, LOW);
    digitalWrite(relay45, LOW);
  }
  else if (user_in == 1) {
    digitalWrite(relay25, HIGH);
    digitalWrite(relay35, LOW);
    digitalWrite(relay45, LOW);
  }
  else if (user_in == 2) {
    digitalWrite(relay25, LOW);
    digitalWrite(relay35, HIGH);
    digitalWrite(relay45, LOW);
  }
  else if (user_in == 3) {
    digitalWrite(relay25, LOW);
    digitalWrite(relay35, LOW);
    digitalWrite(relay45, HIGH);
  }
  else if (user_in == 4) {
    digitalWrite(relay25, HIGH);
    digitalWrite(relay35, HIGH);
    digitalWrite(relay45, LOW);
  }
  else if (user_in == 5) {
    digitalWrite(relay25, HIGH);
    digitalWrite(relay35, LOW);
    digitalWrite(relay45, HIGH);
  }
  else if (user_in == 6) {
    digitalWrite(relay25, LOW);
    digitalWrite(relay35, HIGH);
    digitalWrite(relay45, HIGH);
  }
  else if (user_in == 7) {
    digitalWrite(relay25, HIGH);
    digitalWrite(relay35, HIGH);
    digitalWrite(relay45, HIGH);
  }
}

float calc_degree(int distance) {
  float D0 = 270; // value of distance from tof when door is closed
  float D1 = 480; //value of distance from tof when door is fully open
  return (distance - D0) / ((D1 - D0) / 115); // 115 is max degree door can open from closed position
}
