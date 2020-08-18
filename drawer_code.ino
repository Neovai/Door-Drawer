#include <AccelStepper.h>
#include <MultiStepper.h>
#include "Adafruit_VL53L0X.h"

//reset motor pins
#define pulse_reset 3
#define direction_reset 2

//friction motor pins
#define pulse_friction 9
#define direction_friction 8

//FSR402 data pins (from handle)
#define fsr_1 A0
#define fsr_2 A1
#define fsr_3 A2
#define fsr_4 A3
#define fsr_5 A4
#define fsr_6 A5
#define fsr_7 A6
#define fsr_8 A7
#define fsr_9 A8
#define fsr_10 A9
#define fsr_11 A10
#define fsr_12 A11

AccelStepper reset_motor(1,pulse_reset,direction_reset);
AccelStepper friction_motor(1,pulse_friction, direction_friction);

Adafruit_VL53L0X tof = Adafruit_VL53L0X();
int start_pos; //distance of drawer from tof in starting pos, the '0' position.
const int buffer_val = 5; //buffer value for tof sensor for calculating distance
const float fric_steps = .00032; //constant that represents relation between friction setting to motor steps
const float base_friction = .3; //min resistance that drawer has
const float min_steps = 2500; //min steps it takes to get brake to touch drawer fin
float force_input; //input from user to set resistance rating
char junk = ' ';

const int time_unwind = 4000; //in ms
unsigned long time;
unsigned long time_stop;

void reset_drawer(VL53L0X_RangingMeasurementData_t &measure){
  reset_motor.setSpeed(-5000); //set speed to negative value to change direction
  bool did_move = false;
  while(true){
    tof.rangingTest(&measure, false);
    if(measure.RangeMilliMeter < (start_pos + buffer_val)){
      break;
    }
    did_move = true;
    time = millis();
    time_stop = time + 100; //runs motor for 100ms before checking if drawer is closed
    while(time < time_stop){
      reset_motor.runSpeed();
      time = millis();
    }
  }
  if(did_move){ //if drawer did not move at all (or did not need to be reeled in), don't unwind
   time = millis();
   time_stop = time + time_unwind;
   reset_motor.setSpeed(5000);
   while(time < time_stop){ //unwinds motor so string has slack
     reset_motor.runSpeed();
     time = millis();
    }
  }
}

void set_friction(float resistance){
  float steps = ((resistance - base_friction) / fric_steps) + min_steps;
  //int starting_pos = friction_motor.currentPosition();
 // Serial.print("Starting Position: "); Serial.print(starting_pos); Serial.println();
  friction_motor.setSpeed(5000);
  friction_motor.moveTo(steps);
  friction_motor.setSpeed(5000);
 // Serial.print("Target Position: "); Serial.print(friction_motor.targetPosition()); Serial.println();
 // delay(2000);
  do{
      friction_motor.runSpeed();
  }while(friction_motor.currentPosition() < friction_motor.targetPosition());
}

void reset_friction(){
  friction_motor.setSpeed(-5000);
  friction_motor.moveTo(0);
  friction_motor.setSpeed(-5000); //might need to make negative?
  do{
      friction_motor.runSpeed();
  }while(friction_motor.currentPosition() > friction_motor.targetPosition());
  //Serial.print("Starting Position: "); Serial.print(friction_motor.currentPosition()); Serial.println();
}

void read_handle_val(){
  Serial.print(analogRead(fsr_1)); Serial.print(" ");
  Serial.print(analogRead(fsr_2)); Serial.print(" ");
  Serial.print(analogRead(fsr_3)); Serial.print(" ");
  Serial.print(analogRead(fsr_4)); Serial.print(" ");
  Serial.print(analogRead(fsr_5)); Serial.print(" ");
  Serial.print(analogRead(fsr_6)); Serial.print(" ");
  Serial.print(analogRead(fsr_7)); Serial.print(" ");
  Serial.print(analogRead(fsr_8)); Serial.print(" ");
  Serial.print(analogRead(fsr_9)); Serial.print(" ");
  Serial.print(analogRead(fsr_10)); Serial.print(" ");
  Serial.print(analogRead(fsr_11)); Serial.print(" ");
  Serial.print(analogRead(fsr_12)); Serial.print(" ");
}

void setup() {
  Serial.begin(9600);
  while(!Serial){
    ;
  }
  if (!tof.begin()) { //if tof isn't connected, don't continue program
    Serial.println(F("Failed to boot Time of Flight Sensor (VL53L0X)"));
    while (1);
  }
  
 pinMode(pulse_reset, OUTPUT);
 pinMode(direction_reset, OUTPUT);
 pinMode(pulse_friction, OUTPUT);
 pinMode(direction_friction, OUTPUT);
 friction_motor.setMaxSpeed(20000);
 reset_motor.setMaxSpeed(20000);

 pinMode(fsr_1, INPUT);
 pinMode(fsr_2, INPUT);
 pinMode(fsr_3, INPUT);
 pinMode(fsr_4, INPUT);
 pinMode(fsr_5, INPUT);
 pinMode(fsr_6, INPUT);
 pinMode(fsr_7, INPUT);
 pinMode(fsr_8, INPUT);
 pinMode(fsr_9, INPUT);
 pinMode(fsr_10, INPUT);
 pinMode(fsr_11, INPUT);
 pinMode(fsr_12, INPUT);
}

void loop() {
 Serial.print("Enter Force: ");
 while (Serial.available() == 0); {
   force_input = Serial.parseFloat();
   Serial.print(force_input);
   Serial.print("\n");
   while (Serial.available() > 0) {
     junk = Serial.read();
   }
 }
 set_friction(force_input);

 reset_friction();
 VL53L0X_RangingMeasurementData_t measure; //value from tof sensor
 tof.rangingTest(&measure, false);
 start_pos = measure.RangeMilliMeter; // initialize starting pos of drawer
 
 //for testing purposes only:
 time = millis();
 time_stop = time + 15000;
 
 while(time < time_stop){ // main loop for getting fsr values and pos of drawer
 tof.rangingTest(&measure, false);
 if(measure.RangeMilliMeter <= start_pos){
   Serial.print("Distance Drawer is out: 0mm");
 }
 else{
   Serial.print("Distance Drawer is out: "); Serial.print((measure.RangeMilliMeter - start_pos)); Serial.print("mm");
 }
 
  Serial.print(". Time: "); Serial.print(time);
  read_handle_val();
  Serial.println();
  delay(50);
  time = millis();
 }
 reset_friction();
 reset_drawer(measure);
}
