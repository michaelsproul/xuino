from setuptools import setup

long_description = """Xuino ("zwee-no") is a command-line Arduino toolkit that aims to be simple & C-like.

It facilitates the use of simple makefiles by handling the compilation of the Arduino standard libraries. It also exposes a Python API for use with other tools.

It was inspired by [Ino](https://github.com/amperka/ino) and runs on Linux & OS X."""

setup(
	name = "xuino",

	version = "0.1.1",

	description = "Command-line Arduino toolkit.",

	long_description = long_description,

	url = "https://github.com/michaelsproul/xuino",

	author = "Michael Sproul",

	author_email = "micsproul@gmail.com",

	license = "GPLv3",

	classifiers = [
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"Intended Audience :: Education",
		"Environment :: Console",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
		"Programming Language :: Python :: 3",
		"Topic :: Software Development :: Build Tools",
		"Topic :: Software Development :: Embedded Systems"
	],

	keywords = "arduino build compile avr tool command-line",

	packages = ["xuino"],

	entry_points = {"console_scripts": ["xuino = xuino.xuino:main"]},

	package_data = {"xuino": ["makefiles/*.mk", "makefiles/*/*", "dependencies.json"]},
)
