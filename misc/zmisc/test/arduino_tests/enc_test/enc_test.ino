const int en1 = 3;    //0
const int pwmPin = 4; //5
const int in1 = 5;    //7
const int in2 = 6;    //4
const int clk = 7;
const int dt = 8;
const int csPin = A0;

int motorPwr = 30;

void setup() {
  Serial.begin(4800);
  pinMode(en1, OUTPUT);
  pinMode(pwmPin, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(clk, INPUT);
  pinMode(dt, INPUT);

}

void loop() {
  digitalWrite(en1, HIGH);
  analogWrite(pwmPin, motorPwr);
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);

//  int csVal = analogRead(csPin);
//  Serial.println(csVal);

  bool clkd = digitalRead(clk);
  Serial.print("CLK : ");
  Serial.print(clkd);
  
  bool dtd = digitalRead(dt);
   Serial.print("  DTA : ");
  Serial.println(dtd);

  //    int encTm = pulseIn(sens1, HIGH);
  //    Serial.println(encTm);
}
