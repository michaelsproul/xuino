Squid
=====

Squid is a command-line Arduino toolkit that aims to be simple & C-like.

It facilitates the use of simple makefiles by handling the compilation of the Arduino standard libraries.

It was inspired by [Ino](https://github.com/amperka/ino) and runs on Linux & OS X.

Installation
============

Before you dive into compiling Arduino code, make sure you've installed all of the following dependencies.

* Python 3.3 or later
* Make
* The Arduino Platform, version 1.0.x
* The AVR GNU C compiler: `avr-gcc` on Arch Linux, `gcc-avr` on Debian/Ubuntu
* The AVR Binary Utilities: `avr-binutils` on Arch Linux, `binutils-avr` on Debian/Ubuntu
* The AVR C library: `avr-libc`
* AVR Dude for uploading: `avrdude`
* Picocom for serial communication: `picocom`

The package names may vary depending on your distribution. You might be able to install them all at once by installing an Arduino package.

With that done, clone this git repository and run `sudo make install`. You can adjust Squid's installation directory by editing the Makefile.

Getting Started
===============

To get a feel for how Squid works, lets compile a simple web server.

## Setting Up

First up, grab an Arduino and plug it in via USB. Then, open a terminal in the WebServer example directory.

```
cd examples/WebServer
```

At the moment, this folder just contains standard Arduino code. Let's add a Squid Makefile so we can compile it.

```
squid init
```

The `init` command creates a new makefile from the template at makefiles/Project.mk. It will ask you a few questions about the project you're setting up, and prefill some variables accordingly.

Answer the prompts as follows:

```
Project name: WebServer
Board short name: <your board name>
Libraries: Ethernet
```

Now your WebServer directory should contain two files; WebServer.ino and Makefile. Open up the Makefile to have a look around. Notice in particular how the main executable, $(PROJECT).hex depends on a list of object files. If you're working on a project with lots of source files you can control exactly which ones to compile. Also notice how lots of the variables are filled by calls to `squid`. You could make your project right now simply by running `make`!

## Compiling

Although it's possible to make your project with just plain `make`, Squid also provides a make command that provides better diagnostic output (and is a tiny bit faster).

```
squid make
```

Notice how the SPI library was compiled & linked automatically due to the Ethernet library's dependency on it!

All being well, you should now see a few `.elf`, `.hex` and `.o` files in the current directory. The `.hex` file is the Arduino executable binary, and the others are intermediate object code and can be deleted if you don't mind a bit of recompilation (add `rm *.o *.elf` to the hex making rule).

## Uploading

To upload your code to the Arduino, run `make upload`. You should see avrdude do its thing, and some sort of success message. Open up a browser and go to `192.168.1.225` to see the web page being served by your Arduino!

If you have trouble uploading you may need to manually set the serial port. You can try running `ls /dev/ttyUSB*` to see a list of potentially correct devices which you can try plugging in to the Makefile's `USB_DEVICE` variable.

That's it!

For more information see the [official Squid documentation](http://documentup.com/gnusouth/squid), run `squid --help` from a terminal or run `import squid; help(squid)` from a Python interpreter.

Quick Commands
==============

```
# Create a new makefile
squid init

# Build a project
squid make

# Upload a project
make upload

# Open the serial monitor
make serial

# Alternatively
picocom /dev/ttyUSB0 -b 9600

# Flush out the compiled library cache
squid clean
```

Configuration
=============

Squid reads global configuration from `~/.squidrc` and project-specific configuration from `.squid`.

You can use configuration files to change things like your Arduino directory.

See the example configuration file at `examples/config` for a full list of options.

Contribute
==========

If you like Squid, please help out! If you feel like writing documentation, adding features or reporting bugs, I'm more than happy to accept your [pull requests](https://help.github.com/articles/using-pull-requests). I'm planning to write some documentation on how it all works soon, because one of Squid's main aims is to promote education. You're invited to read the source code and give feedback. My hope is that Squid's source code is easy to understand, and as simply as possible.

Thanks for stopping by!

License
=======

Squid is Free Software licensed under the GNU GPLv3+

&copy; Copyright Michael Sproul 2014.
