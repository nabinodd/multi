#include<Wire.h>

const byte drive_st_reg = 0;
const byte alert_reg = 1;
const byte bat_reg = 2;
const byte limit_reg = 3;

bool bat_qry = false;
bool limit_qry = false;

int bat1 = 80;
int bat2 = 100;

bool limit_u = false;
bool limit_d = true;

bool new_data = false;

byte buff[20];

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
  if (bat_qry) {
    Wire.write(bat1);
    Wire.write(bat2);
    Serial.println("Batt Sent");
  }
  else if (limit_qry) {
    Wire.write(limit_u);
    Wire.write(limit_d);
    Serial.println("Limit Sent");
  }
}

void loop() {
  if (new_data) {
    byte reg_byte = buff[0];
    byte len_byte = buff[1] + 1;

    switch (reg_byte) {
      case bat_reg:
        limit_qry = false;
        bat_qry = true;
        break;
      case (limit_reg):
        limit_qry = true;
        bat_qry = false;
        break;
      case (drive_st_reg):
        Serial.print("Drive State >> ");
        for (int i = 2; i <= len_byte; i++) {
          Serial.print(char(buff[i]));
          Serial.print("");
        }
        break;
      case (alert_reg):
        Serial.print("Alert state >> ");
        for (int i = 2; i <= len_byte; i++) {
          Serial.print(char(buff[i]));
          Serial.print("");
        }
        break;
    }
    Serial.println("\n");
    new_data = false;
  }
}
