#include <SPI.h>
#include <Ethernet.h>
#include <avr/wdt.h>
#include "DHT.h"

// DHT11 sensor pins
#define DHTPIN 7
#define DHTTYPE DHT22

// Delay between sending
#define delayMillis 30000UL

byte mac[] = { 0x90, 0xA2, 0xDA, 0x0E, 0xFE, 0x40 };

// Ethernet client
EthernetClient client;

// Create CC3000 & DHT instances
DHT dht(DHTPIN, DHTTYPE);

// Variables to be exposed to the API
int temperature;
int humidity;

unsigned long thisMillis = 0;
unsigned long lastMillis = 0;

char server[] = "10.0.0.11";
char location[] = "office";

void setup(void)
{
  // Start Serial
  Serial.begin(9600);

  // Start the Ethernet connection and the server
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
  } else {
    Serial.print("My IP: ");
    Serial.println(Ethernet.localIP());
  }

  // Start watchdog
  wdt_enable(WDTO_4S);
}

void loop() {
  thisMillis = millis();
  if(thisMillis - lastMillis > delayMillis) {
    lastMillis = thisMillis;

    // Measure from DHT
    temperature = (uint8_t)dht.readTemperature();
    humidity = (uint8_t)dht.readHumidity();
    
    String payload = "[{";
    payload = payload + "\"name\":\"environment\",\"columns\":[\"temperature\",\"humidity\",\"location\"],";
    payload = payload + "\"points\":[[" + temperature + "," + humidity + ",\"" + location + "\"]]";
    payload = payload + "}]";

    if (client.connect(server, 8086)) {
      Serial.println("connection successful");
      client.println("POST /db/home/series?u=root&p=root HTTP/1.1");
      client.println("User-Agent: arduino-ethernet");
      client.println("Content-Type: application/json");
      client.print("Content-Length: ");
      client.println(payload.length());
      client.println("Connection: close");
      client.println();
      client.println(payload);
      client.println();
      client.stop();
    } else {
      Serial.println("connect failed");
    }
  }

  wdt_reset();
}
