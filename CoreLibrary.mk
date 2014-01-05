# Make file for the core Arduino library

CC = avr-gcc
CXX = avr-g++

BOARD_C_FLAGS = -mmcu=atmega328p -DF_CPU=16000000UL -DARDUINO=105
LIB_C_FLAGS = $(BOARD_C_FLAGS) -Os -w

ARDUINO_DIR = /usr/share/arduino
ARDUINO_CORE = $(ARDUINO_DIR)/hardware/arduino/cores/arduino
BOARD_VARIANT = standard
ARDUINO_VARIANT = $(ARDUINO_DIR)/hardware/arduino/variants/$(BOARD_VARIANT)

VPATH = $(ARDUINO_CORE) $(ARDUINO_CORE)/avr-libc $(ARDUINO_VARIANT)

INCLUDES = -I $(ARDUINO_CORE) -I $(ARDUINO_CORE)/avr-libc -I $(ARDUINO_VARIANT)

LIBOBJS = CDC.o HardwareSerial.o HID.o IPAddress.o main.o Print.o Stream.o \
	  Tone.o USBCore.o WInterrupts.o wiring.o wiring_analog.o \
	  wiring_digital.o wiring_pulse.o wiring_shift.o WMath.o WString.o \
	  malloc.o realloc.o

libarduino.a: $(LIBOBJS)
	avr-ar rcs libarduino.a $^
	rm *.o

%.o: %.cpp
	$(CXX) $(LIB_C_FLAGS) -c -o $@ $< $(INCLUDES)

%.o: %.c
	$(CC) $(LIB_C_FLAGS) -c -o $@ $< $(INCLUDES)

clean:
	rm -rf obj src libarduino.a

.PHONY: default clean
