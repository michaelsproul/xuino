# Make file for the Arduino library

CC = avr-gcc
CXX = avr-g++

BOARD_C_FLAGS ?= -mmcu=atmega328p -DF_CPU=16000000UL -DARDUINO=105
LIB_C_FLAGS = $(BOARD_C_FLAGS) -Os -w

ARDUINO_DIR ?= /usr/share/arduino
ARDUINO_CORE ?= $(ARDUINO_DIR)/hardware/arduino/cores/arduino
BOARD_VARIANT = standard
ARDUINO_VARIANT ?= $(ARDUINO_DIR)/hardware/arduino/variants/$(BOARD_VARIANT)

OBJECTS = CDC.o HardwareSerial.o HID.o IPAddress.o main.o Print.o Stream.o \
	  Tone.o USBCore.o WInterrupts.o wiring.o wiring_analog.o \
	  wiring_digital.o wiring_pulse.o wiring_shift.o WMath.o WString.o \
	  malloc.o realloc.o

LIBOBJS = $(OBJECTS:%.o=obj/%.o)

default: libarduino.a

libarduino.a: $(LIBOBJS)
	avr-ar rcs $(LIBARDUINO) $^

obj/*.o: src/*.c
	mkdir -p obj
	$(CC) $(LIB_C_FLAGS) -c -o $@ $< -I src

obj/*.o: src/*.cpp
	mkdir -p obj
	$(CXX) $(LIB_C_FLAGS) -c -o $@ $< -I src

src/*.c*:
	mkdir -p src
	cp -ru $(ARDUINO_CORE)/* src
	cp -ru $(ARDUINO_CORE)/avr-libc/* src
	cp -ru $(ARDUINO_VARIANT)/* src

clean:
	rm -rf obj src libarduino.a

.PHONY: default clean
