from setuptools import setup

setup(
	name = "xuino",

	version = "0.1.1",

	description = "Command-line Arduino toolkit.",

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
