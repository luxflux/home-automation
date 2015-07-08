// 

#include "DHT.h"
#include <Adafruit_CC3000.h>
#include <ccspi.h>
#include <SPI.h>
#include <string.h>
#include "utility/debug.h"

#define ADAFRUIT_CC3000_IRQ   3
#define ADAFRUIT_CC3000_VBAT  5
#define ADAFRUIT_CC3000_CS    10

#define DHTPIN 7 
#define DHTTYPE DHT22

#define WLAN_SSID "yuxHome"
#define WLAN_PASS "schmidswlan"
#define WLAN_SECURITY WLAN_SEC_WPA2

int photocellPin = 0;
int photocellReading;
int photocellReadingWhenPoweringOn = 0;
int lamp_difference = 0;

int movementPin = 6;
int movement = 0;

int relayPin = 4;

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

Adafruit_CC3000 cc3000 = Adafruit_CC3000(ADAFRUIT_CC3000_CS, ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_VBAT, SPI_CLOCK_DIV2);

#define HOST "influx01.yux.ch"
#define URL "/db/home/series?u=root&p=root"
#define PORT 8086
#define LOCATION "Office"

uint32_t ip;

// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);
  
  Serial.println(F("\nInitializing CC3000..."));
  if (!cc3000.begin())
  {
    Serial.println(F("Couldn't begin()! Check your wiring?"));
    while(1);
  }
  
  Serial.print(F("\nAttempting to connect to ")); Serial.println(WLAN_SSID);
  if (!cc3000.connectToAP(WLAN_SSID, WLAN_PASS, WLAN_SECURITY)) {
    Serial.println(F("Failed!"));
    while(1);
  }
   
  Serial.println(F("Connected!"));
  
  Serial.println(F("Request DHCP"));
  while (!cc3000.checkDHCP())
  {
    delay(100); // ToDo: Insert a DHCP timeout!
  }
  
  while (! displayConnectionDetails()) {
    delay(1000);
  }
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
  

  ip = 0;
  
  // Try looking up the website's IP address
  Serial.print(HOST);
  Serial.print(F(" -> "));
  while (ip == 0) {
    if (! cc3000.getHostByName(HOST, &ip)) {
      Serial.println(F("Couldn't resolve!"));
    }
    delay(500);
  }

  cc3000.printIPdotsRev(ip);
  
  Adafruit_CC3000_Client www = cc3000.connectTCP(ip, PORT);
  if(www.connected()) {
    Serial.println("connection successful");
    Serial.print("Free RAM: "); Serial.println(getFreeRam(), DEC);
    
    String payload = "[{";
    payload = payload + "\"name\":\"environment\",\"columns\":[\"temperature\",\"humidity\",\"location\"],";
    payload = payload + "\"points\":[[" + temperatureReading + "," + humidityReading + ",\"" + LOCATION + "\"]]";
    payload = payload + "}]";
    
    www.println("POST /db/home/series?u=root&p=root HTTP/1.1");
    www.println("User-Agent: arduino-ethernet");
    www.println("Content-Type: application/json");
    www.print("Content-Length: ");
    www.println(payload.length());
    www.println("Connection: close");
    www.println();
    www.println(payload);
    www.println();
    www.close();
    //cc3000.disconnect();
    
    Serial.print("Free RAM: "); Serial.println(getFreeRam(), DEC);

//    char stringBuffer[8];
//    
//    www.fastrprint(F("POST "));
//    www.fastrprint(URL);
//    www.fastrprint(F(" HTTP/1.1\r\n"));
//    www.fastrprint(F("Host: ")); www.fastrprint(HOST); www.fastrprint(F("\r\n"));
//    www.fastrprint(F("\r\n"));
//    www.fastrprint(F("User-Agent: arduino-ethernet\r\n"));
//    www.fastrprint(F("Content-Type: application/json\r\n"));    
//    www.fastrprint(F("Connection: close\r\n"));
//    www.fastrprint(F("Content-Length: "));
//    
//    
//    Serial.print("Free RAM: "); Serial.println(getFreeRam(), DEC);
//    Serial.println(F("Sending content length"));
//    
//    String payload = "[{";
//    payload = payload + "\"name\":\"environment\",\"columns\":[\"temperature\",\"humidity\",\"location\"],";
//    payload = payload + "\"points\":[[" + temperatureReading + "," + humidityReading + ",\"" + LOCATION + "\"]]";
//    payload = payload + "}]";
//    
//    sprintf( stringBuffer, "\"%d\"", payload.length() );
//    www.fastrprint(stringBuffer);
//    www.fastrprint(F("\r\n"));
//    
//    Serial.println(F("Sending payload"));
//    
//    Serial.print("Free RAM: "); Serial.println(getFreeRam(), DEC);
//  
//    www.fastrprint("[{\"name\":\"environment\",\"columns\":[\"temperature\",\"humidity\",\"location\"],\"points\":[[");
//    Serial.println(F("1st line"));
//    Serial.print("Free RAM: "); Serial.println(getFreeRam(), DEC);
//
//    sprintf( stringBuffer, "%d", temperatureReading );
//    www.fastrprint(stringBuffer);
//    Serial.println("temp");
//    www.fastrprint(",");
//    sprintf( stringBuffer, "%d", humidityReading );
//    www.fastrprint(stringBuffer);
//    Serial.println("humidity");
//    sprintf( stringBuffer, "\"%s\"", LOCATION );
//    www.fastrprint(stringBuffer);
//    Serial.println("location");
//    www.fastrprint("]]}]\r\n");
//    Serial.println("end");
//    Serial.println("Stuff sent");
//    Serial.print("Free RAM: "); Serial.println(getFreeRam(), DEC);
  } else {
    Serial.println(F("Connection failed"));
  }
  
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

bool displayConnectionDetails(void)
{
  uint32_t ipAddress, netmask, gateway, dhcpserv, dnsserv;
  
  if(!cc3000.getIPAddress(&ipAddress, &netmask, &gateway, &dhcpserv, &dnsserv))
  {
    Serial.println(F("Unable to retrieve the IP Address!\r\n"));
    return false;
  }
  else
  {
    Serial.print(F("\nIP Addr: ")); cc3000.printIPdotsRev(ipAddress);
    Serial.print(F("\nNetmask: ")); cc3000.printIPdotsRev(netmask);
    Serial.print(F("\nGateway: ")); cc3000.printIPdotsRev(gateway);
    Serial.print(F("\nDHCPsrv: ")); cc3000.printIPdotsRev(dhcpserv);
    Serial.print(F("\nDNSserv: ")); cc3000.printIPdotsRev(dnsserv);
    Serial.println();
    return true;
  }
}
