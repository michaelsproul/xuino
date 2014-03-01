# Generic makefile for both core and non-core Arduino libraries
# Defined externally: BOARD, LIBRARY
# To make the core library, use LIBRARY = core
# DEPENDENCIES should be a space separated list of library names.

CC = avr-gcc
CXX = avr-g++

BOARD_C_FLAGS ?= $(shell xuino get cflags $(BOARD))
C_FLAGS = $(BOARD_C_FLAGS) -Os -w -ffunction-sections -fdata-sections

SRC_DIRS ?= $(shell xuino get src $(LIBRARY) --board $(BOARD))
INCLUDES ?= $(shell xuino get src $(LIBRARY) --board $(BOARD) -I)

VPATH = $(SRC_DIRS)

LIBOBJS ?= $(shell xuino get obj $(LIBRARY))

# Use the lowercased library name for the archive
LIBARCHIVE ?= lib$(shell echo $(LIBRARY) | tr '[:upper:]' '[:lower:]').a

$(LIBARCHIVE): $(LIBOBJS)
	@echo Creating $(LIBARCHIVE) archive.
	@avr-ar rcs $@ $^

%.o: %.cpp
	@echo Compiling $@
	@$(CXX) $(C_FLAGS) -c -o $@ $< $(INCLUDES)

%.o: %.c
	@echo Compiling $@
	@$(CC) $(C_FLAGS) -c -o $@ $< $(INCLUDES)
