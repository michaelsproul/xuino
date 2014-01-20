## Makefile template for Arduino projects
CC = avr-gcc
CXX = avr-g++

PROJECT = Blink
BOARD = atmega328
LIBRARIES = Ethernet SPI

BOARD_FLAGS = $(shell imp boardflags $(BOARD))
BOARD_FLAGS = -mmcu=atmega328p -DF_CPU-16000000UL -DARDUINO=105

DEFAULT_CFLAGS = -Os -w -Wl,--gc-sections -ffunction-sections -fdata-sections
CFLAGS = $(DEFAULT_CFLAGS)



ARDUINO_DIR = /usr/share/arduino
ARDUINO_CORE = $(ARDUINO_DIR)/hardware/arduino/cores/arduino
BOARD_VARIANT = standard
ARDUINO_VARIANT = $(ARDUINO_DIR)/hardware/arduino/variants/$(BOARD_VARIANT)

INCLUDES = -I $(ARDUINO_CORE) -I $(ARDUINO_CORE)/avr-libc -I $(ARDUINO_VARIANT)

# Setup Arduino libraries (Ethernet, etc)
LIBRARIES = $(shell ls -d $(ARDUINO_DIR)/libraries/* $(ARDUINO_DIR)/libraries/*/utility/)
INCLUDES += -I $(shell echo $(LIBRARIES) | sed "s/ / -I /g")
VPATH = $(LIBRARIES)

# Define the directory where the core Arduino library resides
LIBDIR = /home/michael/Programming/imp/



$(PROJECT).hex: $(PROJECT).elf
	avr-objcopy -O ihex $< $@

OBJECTS = $(PROJECT).o Ethernet.o Dhcp.o SPI.o w5100.o EthernetServer.o EthernetClient.o Dns.o EthernetUdp.o socket.o \
	  SD.o File.o Sd2Card.o SdFile.o SdVolume.o Useless.o

$(PROJECT).elf: $(OBJECTS)
	avr-gcc $(BOARD_FLAGS) -fdata-sections -w -Wl,--gc-sections -o $@ $^ -L $(LIBDIR) -larduino -lm
	rm *.o

upload: $(PROJECT).hex
	avrdude -c arduino -p m328p -b 57600 -U flash:w:$< -P/dev/ttyUSB0

%.o: %.ino
	$(CXX) -x c++ $(BOARD_FLAGS) $(CFLAGS) -c -o $@ $< $(INCLUDES)

%.o: %.cpp
	$(CXX) $(BOARD_FLAGS) $(CFLAGS) -c -o $@ $< $(INCLUDES)

%.o: %.c
	$(CC) $(BOARD_FLAGS) $(CFLAGS) -c -o $@ $< $(INCLUDES)

clean:
	rm -f *.o *.hex *.elf
