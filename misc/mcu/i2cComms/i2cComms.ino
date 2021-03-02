#include<Wire.h>

byte drive_st_reg = 0;
byte alert_reg = 1;
byte bat_reg = 2;

bool new_data = false;
byte buff[10];

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
  if (new_data) {
    byte reg_byte = buff[0];
    byte len_byte = buff[1] + 1;
    if (reg_byte == bat_reg);
    else if (reg_byte == drive_st_reg)
    {
      Serial.print("Drive State >> ");
      for (int i = 2; i <= len_byte; i++) {
        Serial.print(char(buff[i]));
        Serial.print("");
      }
    }
    else if (reg_byte == alert_reg)
    {
      Serial.print("Alert state >> ");
      for (int i = 2; i <= len_byte; i++) {
        Serial.print(char(buff[i]));
        Serial.print("");
      }
    }
    Serial.println("\n");
    new_data = false;
  }
}
