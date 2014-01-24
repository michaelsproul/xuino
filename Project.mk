## Makefile template for Arduino projects
CC = avr-gcc
CXX = avr-g++

PROJECT = {PROJECT}
BOARD = {BOARD}
LIBRARIES = # List of libraries to use (case sensitive)

BOARD_C_FLAGS ?= $(shell imp get cflags $(BOARD))
DEFAULT_CFLAGS = -Os -w -Wl,--gc-sections -ffunction-sections -fdata-sections
CFLAGS = $(BOARD_C_FLAGS) $(DEFAULT_CFLAGS)

SRC_DIRS ?= $(shell imp get src $(LIBRARIES) --board $(BOARD))
HEADER_INCLUDES ?= $(shell imp get src $(LIBRARIES) --board $(BOARD) -I)
LIB_INCLUDES ?= $(shell imp get lib $(LIBRARIES) --board $(BOARD) -L -l)

# Add the header folders to the virtual path
VPATH = $(SRC_DIRS)

OBJECTS = $(PROJECT).o

$(PROJECT).hex: $(PROJECT).elf
	avr-objcopy -O ihex $< $@


$(PROJECT).elf: $(OBJECTS)
	avr-gcc $(CFLAGS) -o $@ $^ $(LIB_INCLUDES)
	rm *.o

upload: $(PROJECT).hex
	avrdude -c arduino -p m328p -b 57600 -U flash:w:$< -P/dev/ttyUSB0

%.o: %.ino
	$(CXX) -x c++ $(CFLAGS) -c -o $@ $< $(HEADER_INCLUDES)

%.o: %.cpp
	$(CXX) $(CFLAGS) -c -o $@ $< $(HEADER_INCLUDES)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $< $(HEADER_INCLUDES)

clean:
	rm -f *.o *.hex *.elf
