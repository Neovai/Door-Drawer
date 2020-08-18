// Include the necessary libraries
#include "math.h" //Includes math library
#include <Adafruit_MCP3008.h> //Includes library for SPI communications
#include "Adafruit_VL53L0X.h" //library for time of fligh sensor (tof)

//define pins for motor controller
#define enable_motor_channel 6 //pwm pin
#define motor_channel3  48
#define motor_channel4  42

// define pins for relay/electromagnet
#define relay25 35
#define relay35 33
#define relay45 44

// Initialize FSR and Potentiometer in door frame
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
float magnet_input;
float time_input;
float trial_input;
char junk = ' ';
unsigned long time;
unsigned long stoptime;

//declare motor variable for time
const int time_unwind = 2000; // in ms

void Reset_Door() {
  bool did_move = false;
  int motor_speed = 100; //max speed for the motor
  Enable_Relays(0); // turns off magnets; makes motor faster
  analogWrite(enable_motor_channel, motor_speed); //turns motor on
  digitalWrite(motor_channel3, LOW);// turns motor
  digitalWrite(motor_channel4, HIGH); // counter clockwise
  while (true) { // door is open more than 5 degrees
    VL53L0X_RangingMeasurementData_t measure; //value from tof sensor
    tof.rangingTest(&measure, false);
    door_angle = calc_degree(measure.RangeMilliMeter);
    if (door_angle < 1) {
      break;
    }
    did_move = true;
    delay(100);
  }
  if (did_move) {
    digitalWrite(motor_channel3, HIGH); // turns motor
    digitalWrite(motor_channel4, LOW);// clockwise
    delay(time_unwind); //run for certain amount of time
  }
  analogWrite(enable_motor_channel, 0); // turns motor off
}

void Enable_Relays(int user_in) {
  int relay25_val = 0; //for testing purposes
  if (user_in == 0) {
    digitalWrite(relay25, relay25_val);
    delay(100);
    digitalWrite(relay35, LOW);
    delay(100);
    digitalWrite(relay45, LOW);
    delay(100);
  }
  else if (user_in == 1) {
    digitalWrite(relay25, (relay25_val + 1));
    delay(100);
    digitalWrite(relay35, LOW);
    delay(100);
    digitalWrite(relay45, LOW);
    delay(100);
  }
  else if (user_in == 2) {
    digitalWrite(relay25, relay25_val);
    delay(100);
    digitalWrite(relay35, HIGH);
    delay(100);
    digitalWrite(relay45, LOW);
    delay(100);
  }
  else if (user_in == 3) {
    digitalWrite(relay25, relay25_val);
    delay(100);
    digitalWrite(relay35, LOW);
    delay(100);
    digitalWrite(relay45, HIGH);
    delay(100);
  }
  else if (user_in == 4) {
    digitalWrite(relay25, (relay25_val + 1));
    delay(100);
    digitalWrite(relay35, HIGH);
    delay(100);
    digitalWrite(relay45, LOW);
    delay(100);
  }
  else if (user_in == 5) {
    digitalWrite(relay25, (relay25_val + 1));
    digitalWrite(relay35, LOW);
    digitalWrite(relay45, HIGH);
  }
  else if (user_in == 6) {
    digitalWrite(relay25, relay25_val);
    digitalWrite(relay35, HIGH);
    digitalWrite(relay45, HIGH);
  }
  else if (user_in == 7) {
    digitalWrite(relay25, (relay25_val + 1));
    delay(100);
    digitalWrite(relay35, HIGH);
    delay(100);
    digitalWrite(relay45, HIGH);
    delay(100);
  }
}

float calc_degree(int distance) {
  float D0 = 289; // value of distance from tof when door is closed
  float D1 = 418; //value of distance from tof when door is fully open
  return (distance - D0) / ((D1 - D0) / 90); // 90 is max degree door can open from closed position
}

void get_magnet_val() {
  Serial.print("Enter desired force rating on a scale of 0 to 7: ");
  while (Serial.available() == 0); {
    magnet_input = Serial.parseFloat();
    Serial.print(magnet_input, 0);
    Serial.print("\n");
    while (Serial.available() > 0) {
      junk = Serial.read();
    }
  }
}

void get_trial_length() {
  Serial.print("Enter How long you would like to run each test (in seconds): ");
  while (Serial.available() == 0); {
    time_input = Serial.parseFloat();
    Serial.print(time_input, 0);
    Serial.print("\n");
    while (Serial.available() > 0) {
      junk = Serial.read();
    }
  }
}

void get_num_trials() {
  Serial.print("Enter How many tests you would like to run: ");
  while (Serial.available() == 0); {
    trial_input = Serial.parseFloat();
    Serial.print(trial_input, 0);
    Serial.print("\n");
    while (Serial.available() > 0) {
      junk = Serial.read();
    }
  }
}

void read_handle_val() {
  for (int chan = 0; chan < 8; chan++) { //reads all 16 channels from mcp3008 chips
    Serial.print(adc1.readADC(chan));
    Serial.print("\t");
    Serial.print(adc2.readADC(chan));
    Serial.print("\t");
  }
}

void read_pull_force() {
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
}

void read_TOF_val() {
  VL53L0X_RangingMeasurementData_t measure; //value from tof sensor. pointer
  tof.rangingTest(&measure, false);
  if (measure.RangeStatus != 4) {  // phase failures have incorrect data
    door_angle = calc_degree(measure.RangeMilliMeter);
    Serial.print("Angle of Door (deg): "); Serial.print(door_angle); Serial.print(" ");
    //Serial.print("Distance (mm): "); Serial.println(measure.RangeMilliMeter); //used for calibrating tof sensor
  } else {
    Serial.println(" out of range ");
  }
}

/*----------------- Main Code --------------------*/

void setup() {
  // Initialize the Serial monitor
  Serial.begin(115200);
  while (!Serial);
  //don't run door if TOF is not working
  if (!tof.begin()) {
    Serial.println(F("Failed to boot VL53L0X"));
    while (1);
  }

  // Begins the SPI devices and declares the pins in order of (CLK, MOSI, MISO, CS)
  adc1.begin(52, 51, 50, 53);
  adc2.begin(9, 11, 10, 12);
  // initialize motor pins as outputs
  pinMode(motor_channel3, OUTPUT);
  pinMode(motor_channel4, OUTPUT);
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
  //Temporary Interface for Door testing purposes.
  get_magnet_val();
  get_trial_length();
  get_num_trials();

  for (int i = 1; i <= trial_input; i++) { // runs number of trials
    Serial.print("------- trial ");
    Serial.print(i);
    Serial.print(" -------");
    Serial.print("\n");
    Enable_Relays(magnet_input); // changes electromagnets based on input
    time = millis();
    stoptime = time + (time_input * 1000); // converts time_input to seconds
    while (time < stoptime) {
      read_TOF_val();
      read_handle_val();
      read_pull_force();
      //Turns off electromagnets when not being used.
      //saves energy and reduces heat from electromagnets.
      if (door_angle > 15) {
        Enable_Relays(0);
      }
      else {
        Enable_Relays(magnet_input);
      }
      delay(50);
      time = millis();
    }
    Reset_Door(); // automatically close door
  }
}
