// 

#include "DHT.h"
//#include <Adafruit_CC3000.h>
//#include <SPI.h>
//#include <CC3000_MDNS.h>

//#define ADAFRUIT_CC3000_IRQ   4
//#define ADAFRUIT_CC3000_VBAT  5
//#define ADAFRUIT_CC3000_CS    10

#define DHTPIN 3 
#define DHTTYPE DHT22

//#define WLAN_SSID "yuxHome"
//#define WLAN_PASS "schmidswlan"
//#define WLAN_SECURITY WLAN_SEC_WPA2

int photocellPin = 0;
int photocellReading;
int photocellReadingWhenPoweringOn = 0;
int lamp_difference = 0;

int movementPin = 2;
int movement = 0;

int relayPin = 13;

int thresholdOnOffPin = 1;
int thresholdOnOff;

int thresholdMaxPin = 2;
int thresholdMax;

int uvPin = 4;
int uvReading;

boolean on = false;

DHT dht(DHTPIN, DHTTYPE);
int temperatureReading;
int humidityReading;

//Adafruit_CC3000 cc3000 = Adafruit_CC3000(ADAFRUIT_CC3000_CS, 
//ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_VBAT, SPI_CLOCK_DIV2);

//MDNSResponder mdns;

// the setup function runs once when you press reset or power the board
void setup() {
  pinMode(relayPin, OUTPUT);
  //pinMode(movementPin, INPUT);
  //pinMode(thresholdOnOffPin, INPUT);
  //pinMode(thresholdMaxPin, INPUT);
  pinMode(uvPin, INPUT);
  
  digitalWrite(relayPin, LOW);
  
  Serial.begin(9600);
}

void loop() {
  photocellReading = analogRead(photocellPin);
  movement = digitalRead(movementPin);
  thresholdOnOff = analogRead(thresholdOnOffPin);
  thresholdMax = analogRead(thresholdMaxPin);
  uvReading = analogRead(uvPin);
  temperatureReading = (uint8_t)dht.readTemperature();
  humidityReading = (uint8_t)dht.readHumidity();
 
  Serial.println("============================================");
  Serial.print("Analog reading = ");
  Serial.println(photocellReading);
  Serial.print("Lamp difference = ");
  Serial.println(lamp_difference);
  Serial.print("Movement = ");
  Serial.println(movement);
  Serial.print("current helligkeit ohne lampe = ");
  Serial.println(photocellReading - lamp_difference);
  Serial.print("thresholdOnOff = ");
  Serial.println(thresholdOnOff);
  Serial.print("thresholdMax = ");
  Serial.println(thresholdMax);
  Serial.print("uvReading = ");
  Serial.println(uvReading);
  Serial.print("temperatureReading = ");
  Serial.println(temperatureReading);
  Serial.print("humidityReading = ");
  Serial.println(humidityReading);
  Serial.print("Lamp is on: ");
  Serial.println(on);
  
  if(movement && photocellReading - lamp_difference <= thresholdOnOff) {
    if(!on) {
      digitalWrite(relayPin, HIGH);
      delay(500);
      photocellReadingWhenPoweringOn = analogRead(photocellPin);
      Serial.print("photocellReadingWhenPoweringOn = ");
      Serial.println(photocellReadingWhenPoweringOn);
      lamp_difference = photocellReadingWhenPoweringOn - photocellReading;
      on = true;
    } else {
       //  zu hell               oder  noch heller geworden
       if(photocellReading >= thresholdMax || photocellReading - lamp_difference > thresholdOnOff) {
          lamp_difference = 0;
          on = false;
          digitalWrite(13, LOW);
       }
    }
  } else {
    lamp_difference = 0;
    on = false;
    digitalWrite(relayPin, LOW);
  }
 
  delay(2000);
}
