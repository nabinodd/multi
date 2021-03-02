#include<Wire.h>

bool new_data = false;
byte buff[256];

int bat1 = 80;
int bat2 = 100;

void setup() {
  Serial.begin(115200);
  Wire.begin(9);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
}

void receiveEvent(int data) {
  int c = 0;
  new_data = true;
  while (Wire.available()) {
    buff[c] = Wire.read();
    c++;
  }
}

void requestEvent() {
  Wire.write(bat1);
  Wire.write(bat2);
  Serial.println("Sent");
}

void loop() {
  if (buff[0] == 5);
  else {
    if (new_data) {
      byte reg_byte = buff[0];
      byte len_byte = buff[1] + 1;
      Serial.print("Speed : ");
      for (int i = 2; i <= len_byte; i++) {
        Serial.print(char(buff[i]));
        Serial.print("");
      }
      Serial.println("");
      new_data = false;
    }
  }
}
