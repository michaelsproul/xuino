#include <Arduino.h>
#include "testlibrary.h"

void setup()
{
	Serial.begin(9600);
}

void loop()
{
	Serial.println(TestLibrary::magic_number);
	delay(1000);
}
