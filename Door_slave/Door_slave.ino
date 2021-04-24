#include <Wire.h>
#define angle_opto 2
#define dir_opto 3
unsigned char angle = 0; //assumes door is starting closed
bool prev_angle;
bool prev_dir;

void setup() {
  Wire.begin(2); //address
  Wire.onRequest(request_angle);
  //set opto relays as inputs
  pinMode(angle_opto, INPUT);
  pinMode(dir_opto, INPUT);
}

/*
 * Explanation:
 * The direction opto is positioned at the edge of a filled slot
 * while the angle opto starts centered at a non-filled slot. If
 * the door closes then dir opto will switch states. If
 * the door opens the dir opto will stay the same state.
 * This only works under the assumption that the dir opto is positioned
 * to be at the edge of a slot when the angle opto is at the center of
 * a slot.
 */

void loop() {
  prev_angle = digitalRead(angle_opto);
  prev_dir = digitalRead(dir_opto);
  if(digitalRead(angle_opto) != prev_angle){
    //depends on if dir opto starts on right edge or left edge of slot
    if(digitalRead(dir_opto) != prev_dir){ // door is opening
      angle++;
    }
    else{ //door is closing
      angle--;
    }
  }
}

void request_angle(){
  Wire.write(angle); //sending over one byte
}
