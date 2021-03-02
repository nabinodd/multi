#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include<string.h>

const int trigPin = D1;  //D4
const int echoPin = D2;  //D3
long duration=0;
int distance=0;
int percent=0;
int average=0;
int status=0;
int sum=0;
int reed_value=0;

int analog_in=0;//for battery status
float r1=15;
float r2=69;
int sum1=0;
//float vin=0;
//float vout=0;
float avg_battery_value=0;


// Update these with values suitable for your network.

const char* ssid = "InG R&D";
const char* password = "ONETWOTHREEFOUR";
const char* mqtt_server = "192.168.100.125";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
char bat[50];
int value = 0;

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("dustbin/db1", "data");
      // ... and resubscribe
      //client.subscribe("inTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  pinMode(D5,INPUT);// read reed switch 
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  pinMode(A0,INPUT);//battery read
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

 if (!client.connected()) {
    reconnect();
  }
  client.loop();
//////////////////////////

 bool reed_value = digitalRead(D5);
 Serial.println(reed_value);


  if (reed_value == 0)
  {
   // Serial.println("open");
  Serial.println("esp is sleeping for 15 sec");
  ESP.deepSleep(5e6); //sleep mode for node mcu
    
  }

  if (reed_value == 1) {
    //Serial.println("closed");
  battery_check();
  publish_data();
  delay(3000);
   
 Serial.println("esp is sleeping for 15 sec");
 ESP.deepSleep(5e6); //sleep mode for node mcu
  
  }

  delay(100);
///////////////  
  
 
// 
// Serial.println("esp is sleeping for 15 sec");
// ESP.deepSleep(5e6); //sleep mode for node mcu
}


void loop() {

}

void us()
{
    digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2;
}

void publish_data()
{
  sum=0;
  for(int i =1;i<=5;i++){//average calculation

    us();
    sum+=distance;
    delay(200);
}
  average=sum/5;

  percent = average*100/57;//size of dustbin in cm
  if(percent<=100 && percent>=0){
  status=map(percent,5,95,100,0);
 // battery_check();
  snprintf (msg, 50, "dustbin status=%ld ", status);
  strcat(msg,"%");
  client.publish("dustbin/db1", msg);

  delay(100);
  }
}

void battery_check()//check battery status and publish data
{
  sum1=0;
    for(int i=1;i<=10;i++){
     analog_in= analogRead(A0);
     sum1+=analog_in;
     }

    float avg_battery_value=sum1/10;
    float vout=(avg_battery_value*3.4)/1024;
    float vin=vout/(r2/(r1+r2));
    Serial.print("status=");
    Serial.print(vin);
   Serial.println("v");
   char volt[20]= "Battery voltage=";
   //snprintf (bat, 50, "battery voltage=%ld V", vin);
   dtostrf(vin,4,2,bat);
   strcat(bat,"V");
   strcat(volt,bat);
   client.publish("dustbin/db1", volt);
   delay(10);
   return;
}
