int uvSensorPin = 1;
int uvSensorReading;
int uvIndex;

void setup() {
  //pinMode(uvSensorPin, INPUT);
  
  Serial.begin(9600);
}

void loop() {
  uvSensorReading = analogRead(uvSensorPin);
  uvIndex = uvSensorReading * 0.1;
  
  Serial.print("uvSensorReading = ");
  Serial.println(uvSensorReading);
  Serial.print("uvIndex = ");
  Serial.println(uvIndex);
  
  delay(800);
}
