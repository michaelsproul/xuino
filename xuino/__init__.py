"""Xuino Arduino toolkit by Michael Sproul, Copyright 2014.

Github: https://github.com/michaelsproul/xuino

Licensed under the terms of the GNU GPLv3+
See: https://www.gnu.org/licenses/gpl.html
"""

__author__ = "Michael Sproul <micsproul@gmail.com>"
__version__ = "0.1.1"
__license__ = "GPLv3+"

__all__ = [
	"read_config",
	"read_arduino_ver",
	"read_boards",
	"clean",
	"list_boards",
	"get_cflags",
	"get_src",
	"get_obj",
	"resolve_dependencies",
	"get_lib",
	"make",
	"config"
]

from .xuino import (
	read_config,
	read_arduino_ver,
	read_boards,
	clean,
	list_boards,
	get_cflags,
	get_src,
	get_obj,
	resolve_dependencies,
	get_lib,
	make,
	config
)
