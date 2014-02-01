from setuptools import setup

setup(	name="squid",
	version="0.1a",
	description="Command-line Arduino toolkit.",
	url="https://github.com/gnusouth/squid",
	author="Michael Sproul",
	author_email="micsproul@gmail.com",
	license="GNU General Public License v3 or later",
	packages=["squid"],
	scripts=["bin/squid"],
	long_description=open("README.rst").read(),
	classifiers=[	"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
			"Environment :: Console",
			"Topic :: Education",
			"Topic :: Software Development :: Build Tools",
			"Topic :: Software Development :: Embedded Systems",
			"Intended Audience :: Education",
			"Intended Audience :: Developers"
	]
)
