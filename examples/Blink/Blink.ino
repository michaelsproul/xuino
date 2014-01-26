#include <Arduino.h>

#define LED_PIN 13

#define name(x) ((x == 1) ? "ON" : "OFF")

int STATES[] = {0, 1, 0, 1, 1};
int counter = 0;

void setup()
{
	pinMode(LED_PIN, OUTPUT);
	Serial.begin(9600);
}

void loop()
{
	digitalWrite(LED_PIN, STATES[counter]);
	Serial.println(name(STATES[counter]));
	counter = (counter + 1) % 5;
	delay(1000);
}
