#include <AccelStepper.h>
#include <MultiStepper.h>
#include "Adafruit_VL53L0X.h"

//reset motor pins
#define pulse_reset 3
#define direction_reset 2

//friction motor pins
#define pulse_friction 9
#define direction_friction 8

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

 Serial.print("Press Enter to Stop");
 while (Serial.available() == 0); {
   force_input = Serial.parseFloat();
   //Serial.print(force_input, 0);
   Serial.print("\n");
   while (Serial.available() > 0) {
     junk = Serial.read();
   }
 }
 reset_friction();
 VL53L0X_RangingMeasurementData_t measure; //value from tof sensor
 tof.rangingTest(&measure, false);
 start_pos = measure.RangeMilliMeter; // initialize starting pos of drawer
 //for testing purposes only:
 time = millis();
 time_stop = time + 15000;
 while(time < time_stop){ // main loop for getting fsr values and pos of drawer
 time = millis();
 tof.rangingTest(&measure, false);
 if(measure.RangeMilliMeter <= start_pos){
   Serial.print("Distance Drawer is out: 0mm");
 }
 else{
   Serial.print("Distance Drawer is out: "); Serial.print((measure.RangeMilliMeter - start_pos)); Serial.print("mm");
 }
  Serial.print(". Time: "); Serial.print(time);
  Serial.println();
  delay(50);
 }
 reset_friction();
 reset_drawer(measure);
 }
