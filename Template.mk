# Makefile template for Arduino projects

CXX = avr-g++

BOARD_FLAGS = -mmcu=atmega328p -DF_CPU-16000000UL -DARDUINO=105
CFLAGS = -Os -w -Wl,--gc-sections -ffunction-sections -fdata-sections -x c++

ARDUINO_DIR = /usr/share/arduino
ARDUINO_CORE = $(ARDUINO_DIR)/hardware/arduino/cores/arduino
BOARD_VARIANT = standard
ARDUINO_VARIANT = $(ARDUINO_DIR)/hardware/arduino/variants/$(BOARD_VARIANT)

INCLUDES = -I $(ARDUINO_CORE) -I $(ARDUINO_CORE)/avr-libc -I $(ARDUINO_VARIANT)

LIBDIR = /home/michael/Programming/imp/

PROJECT = blink

$(PROJECT).hex: $(PROJECT).elf
	avr-objcopy -O ihex $< $@

$(PROJECT).elf: blink.ino
	$(CXX) $(BOARD_FLAGS) $(CFLAGS) -o $@ $^ $(INCLUDES) -L $(LIBDIR) -larduino -lm

upload: $(PROJECT).hex
	avrdude -c arduino -p m328p -b 57600 -U flash:w:blink.hex -P/dev/ttyUSB0
