// spider-bot-8 by DRODI | MIT licence | https://github.com/awd1779/spider-bot-8
// P1 - I2C scanner
// Finds every I2C device on SDA / SCL and prints its address.
// The PCA9685 servo module should show up as 0x40.
// ESP32: SDA = GPIO 21, SCL = GPIO 22

#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin();
  delay(500);
  Serial.println("Scanning I2C...");
}

void loop() {
  int found = 0;
  for (int address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {        // 0 = a device answered
      Serial.print("Found a device at 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
      found++;
    }
  }
  if (found == 0) Serial.println("Nothing found. Check VCC, GND, SDA and SCL.");
  Serial.println("---");
  delay(3000);                                 // scan again every 3 seconds
}
