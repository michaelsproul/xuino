"""Xuino Arduino toolkit by Michael Sproul, Copyright 2014.

Github: https://github.com/michaelsproul/xuino

Licensed under the terms of the GNU GPLv3+
See: https://www.gnu.org/licenses/gpl.html
"""

import os
import re
import io
import sys
import glob
import json
import shutil
import argparse
import subprocess
import configparser
import pkg_resources as pkg

# Load Xuino's dependency map
dependency_string = pkg.resource_string(__name__, "dependencies.json").decode()
dependency_string = io.StringIO(dependency_string)
dependency_map = json.load(dependency_string)
dependency_map = {lib: set(deps) for (lib, deps) in dependency_map.items()}

# Global configuration object, initialised later
config = None

# The math library's name
math_library = "m"

# Track whether the code is being run as an executable
running_standalone = False

# The commands beginning with an underscore are called from the command-line.
# The non-underscored versions are the ones that take sensible arguments
# and do all of the actual work.

def _error(message):
	"""Quit the program if running stand alone, or raise an exception otherwise."""
	if running_standalone:
		print("Error: " + message)
		sys.exit(1)
	print("__name__ = {}".format(__name__))
	raise Exception(message)


def read_config():
	"""Read xuino config from ~/.xuinorc and .xuino

	Values in .xuino override those in ~/.xuinorc
	"""
	parser = configparser.ConfigParser()

	# Load defaults
	defaults = {"xuino": {	"arduino_root": "/usr/share/arduino",
							"arduino_ver": "",
							"compile_root": "~/.xuino/",
							"library_dirs": ""
	}}

	parser.read_dict(defaults)

	# Read ~/.xuinorc
	xuinorc = os.path.expanduser("~/.xuinorc")
	if os.path.exists(xuinorc):
		parser.read(xuinorc)

	# Read .xuino
	dotxuino = os.path.abspath(".xuino")
	if os.path.exists(dotxuino):
		parser.read(dotxuino)

	config = dict(parser["xuino"])

	# Expand paths
	config["arduino_root"] = os.path.expanduser(config["arduino_root"])
	config["compile_root"] = os.path.expanduser(config["compile_root"])

	# Convert the space separated list of library directories into a list
	library_dirs = []
	for lib_dir in config["library_dirs"].split():
		lib_dir = os.path.abspath(os.path.expanduser(lib_dir))
		library_dirs.append(lib_dir)

	config["library_dirs"] = library_dirs

	# Figure out the Arduino library version
	if config["arduino_ver"] == "":
		config["arduino_ver"] = read_arduino_ver(config["arduino_root"])
	else:
		# Convert the version to an integer
		config["arduino_ver"] = int(config["arduino_ver"].replace(".", ""))

	return config


def read_arduino_ver(arduino_root):
	"""Extract the Arduino software version from the given root directory."""
	version_path = os.path.join(arduino_root, "lib", "version.txt")

	if not os.path.isfile(version_path):
		m = "Unable to find version.txt\n" \
			"Please explicitly specify a version in ~/.xuinorc or .xuino"
		_error(m)

	with open(version_path, "r") as version_file:
		version = version_file.read().strip()

	try:
		version = int(version.replace(".", ""))
		return version
	except ValueError:
		m = "Unable to parse version number.\n" \
			"Please explicitly specify a version in ~/.xuinorc or .xuino"
		_error(m)


def read_boards():
	"""Parse boards.txt and return a dictionary.

	The module-level `config' object is used to locate the file.
	"""
	boards = {}
	arduino_root = config['arduino_root']
	arduino_ver = config['arduino_ver']

	if arduino_ver < 150:
		filepath = "hardware/arduino/boards.txt"
	else:
		filepath = "hardware/arduino/avr/boards.txt"
	filepath = os.path.join(arduino_root, filepath)

	with open(filepath, "r") as f:
		for line in f:
			if line[0] in "\n#":
				continue

			(key, value) = line.strip().split("=")
			key = key.split(".")
			board = key[0]
			property = ".".join(key[1:])
			if board not in boards:
				boards[board] = {}
			boards[board][property] = value

	return boards


def _init(args):
	"""Create a new project makefile from the template.

	The makefile will be created in the current directory, or the
	directory specified by the `dir' argument to `xuino init'.

	The makefile will be named Makefile and will not be created if
	a file with this name already exists.
	"""
	project_dir = os.path.abspath(args.dir)

	# Check for an existing Makefile
	makefile_path = os.path.join(project_dir, "Makefile")
	if os.path.exists(makefile_path):
		if args.dir == ".":
			message = "Makefile exists!"
		else:
			message = "%s exists!" % makefile_path
		_error(message)

	# Read boards.txt
	boards = read_boards()

	# Request a project name
	project = ""
	while project == "":
		project = input("Project name: ").strip()

	# Request a board to compile for
	print("Please select a board: ")
	list_boards(boards)
	while True:
		board = input("Board short name: ").strip()
		if board in boards:
			break
		print("Invalid. Please pick a board (you can change later).")

	# Request dependent libraries
	print("If your project has dependent libraries, list them here (space separated).")
	libraries = input("Libraries: ")

	# Inject everything into the makefile template
	makefile = pkg.resource_string(__name__, "makefiles/Project.mk").decode()
	makefile = makefile.replace("{PROJECT}", project)
	makefile = makefile.replace("{BOARD}", board)
	makefile = makefile.replace("{LIBRARIES}", libraries)

	# Write the makefile
	with open(makefile_path, "w") as f:
		f.write(makefile)

	print("Successfully created a new makefile.")


def _clean(args):
	clean()


def clean():
	"""Remove everything from the cache of compiled library code.

	This function just deletes config["compile_dir"].
	"""
	shutil.rmtree(config["compile_root"])


def _list_boards(args):
	"""List all available boards from boards.txt"""
	boards = read_boards()
	list_boards(boards)


def list_boards(boards):
	"""Pretty print a list of boards in alphabetical order."""
	board_names = sorted(boards.keys(), key = lambda x: x.lower())
	for board in board_names:
		spacer = "\t\t" if len(board) < 8 else "\t"
		print("%s%s'%s'" % (board, spacer, boards[board]["name"]))


def _get_property(args):
	"""Print the board property requested on the command-line.

	A property is just a bit of information from the Arduino library's
	collection of hardware specific information - "boards.txt".

	Throughout Imp, the names from "boards.txt" are split into a
	board name and a "property".

	Example:
	If the board is "atmega328" and property is "build.f_cpu"
	the value of "atmega328.build.f_cpu" will be fetched.
	"""
	boards = read_boards()
	key = args.property.split(".")
	board = key[0]
	subprop = ".".join(key[1:])
	print(boards[board][subprop])


def _get_cflags(args):
	"""Command-line front-end for get_cflags."""
	boards = read_boards()
	cflags = get_cflags(args.board, boards)
	print(cflags)


def get_cflags(board, boards):
	"""Get the C compiler flags for the given board.

	The flags returned are of the form:
		-mmcu=<mcu> -DF_CPU=<cpu freq> -DARDUINO=<version>
	"""
	board_info = boards[board]
	flags = "-mmcu=%(build.mcu)s -DF_CPU=%(build.f_cpu)s" % board_info
	flags += " -DARDUINO=%s" % config["arduino_ver"]
	return flags


def _get_src(args):
	"""Print a list of source directories for the requested libraries.

	This is a front-end to get_src that also resolves dependencies.

	The source directories can optionally be separated by -I to form a string
	suitable for appending to GCC.
	"""
	# If the board argument is provided, read boards.txt to get variant
	if args.board:
		boards = read_boards()
		variant = boards[args.board]["build.variant"]
	else:
		variant = "standard"

	# Get the list of libraries including dependencies
	libraries = resolve_dependencies(args.libraries)

	# Fetch the source code directories
	src_dirs = get_src(libraries, variant)

	if args.dash_i:
		output = "-I " + " -I ".join(src_dirs)
	else:
		output = " ".join(src_dirs)

	print(output)


def get_src(libraries, variant):
	"""Return a list of directories containing relevant source code.

	By relevant source code, we mean source code for those libraries listed
	in the `libraries' argument (a list). Dependencies are *not* included and
	the core Arduino library is only included if "core" is in the list of libraries.

	If the core library is requested, `variant' is the type of
	Arduino board to compile for. Most boards are just "standard".

	An exception is thrown if the list contains non-existant libraries.
	"""
	src_dirs = []
	root = config["arduino_root"]

	# Sub-function to get the core library
	def get_core():
		core = os.path.join(root, "hardware/arduino/cores/arduino")
		core_sub_dirs = glob.glob("%s/*/" % core)
		var_dir = os.path.join(root, "hardware/arduino/variants/%s" % variant)
		return core_sub_dirs + [core, var_dir]

	# Add requested libraries
	for lib in libraries:
		# Treat the core library carefully
		if lib == "core":
			src_dirs.extend(get_core())
			continue

		# Treat the math library carefully
		if lib == math_library:
			continue

		# Look for the library in root/libraries/name and the user specified directories
		potential_locations = [os.path.join(user_dir, lib) for user_dir in config["library_dirs"]]
		potential_locations.append(os.path.join(root, "libraries", lib))

		for lib_dir in potential_locations:
			if os.path.isdir(lib_dir):
				lib_main = lib_dir
				break
		else:
			_error("No library found with name '%s'" % lib)

		src_dirs.append(lib_main)

		lib_util = os.path.join(lib_main, "utility")
		if os.path.exists(lib_util):
			src_dirs.append(lib_util)

	return src_dirs


def _get_obj(args):
	"""Print the names of all the .o files for a given library."""
	library = args.library

	# Convert the library name into a list of directories
	if library == "core":
		# XXX: This takes advantage of the fact that the variant
		# folders only include headers. Might need to be updated.
		library_dirs = get_src(["core"], "n/a")
	else:
		library_dirs = get_src([library], "n/a")

	objects = get_obj(library_dirs)
	print(" ".join(objects))


def get_obj(library_dirs):
	"""Get the names of all the .o files in the given directories."""
	# Filter function, to turn source filepaths into object filenames
	obj_filter = lambda x, ext: x.split("/")[-1].replace(ext, ".o")

	# Find objects for each directory in the input
	objects = []
	for directory in library_dirs:
		for ext in [".c", ".cpp", "ino"]:
			files = glob.glob("{:s}/*{:s}".format(directory, ext))
			objects.extend([obj_filter(x, ext) for x in files])

	return objects


def resolve_dependencies(libraries):
	"""Given a list of libraries, determine all of their dependencies.

	Return a list of the original libraries, plus their dependencies, ordered
	such that each library comes before all of its dependencies (a topological sort).

	Dependencies are read from dependencies.py in the Xuino installation directory.
	"""
	# If no libraries are required, just return the core library
	if libraries == []:
		return ["core"]

	# Construct a dependency graph.
	# For each library store out-links (to dependencies) and in-links (from dependencies)
	graph = {}
	active_pool = {lib for lib in libraries}
	while len(active_pool) > 0:
		new_pool = set()
		for lib in active_pool:
			# Fetch the set of dependencies
			if lib in dependency_map:
				dependencies = dependency_map[lib]
			else:
				dependencies = set()

			# Add the implicit dependency on the core library
			if lib != "core" and lib != math_library:
				dependencies.add("core")

			# Add the library to the graph
			if lib in graph:
				graph[lib]["out"] = dependencies
			else:
				graph[lib] = {"in": set(), "out": dependencies}

			# Add each dependency to the graph and the active pool if need be
			for dep in dependencies:
				if dep in graph:
					graph[dep]["in"].add(lib)
				else:
					graph[dep] = {"in": {lib}, "out": set()}
					new_pool.add(dep)
		active_pool = new_pool

	# Perform a topological sort on the graph
	library_list = []
	no_inlinks = {node for node in graph if len(graph[node]["in"]) == 0}
	while len(no_inlinks) > 0:
		node = no_inlinks.pop()
		library_list.append(node)

		# Remove it from the graph
		for dep in graph[node]["out"]:
			graph[dep]["in"].remove(node)
			if len(graph[dep]["in"]) == 0:
				no_inlinks.add(dep)
		del graph[node]

	# Check for success
	if len(graph) == 0:
		return library_list
	else:
		_error("Cyclic dependencies!")


def _get_lib(args):
	"""Print a list of directories containing compiled versions of the given libraries.

	Dependencies *are* resolved.
	"""
	boards = read_boards()
	board = args.board
	libraries = args.libraries

	# Resolve dependencies
	libraries = resolve_dependencies(libraries)

	# Make the libraries
	library_list, output = get_lib(libraries, board, boards)

	# Print make output if desired
	if args.verbose:
		for lib in output:
			print("-- Output from %s make command --" % lib)
			print(output[lib])

	# Create the output string, with appropriate separators
	if args.dash_big_l:
		library_string = "-L " + " -L ".join(library_list)
	else:
		library_string = " ".join(library_list)

	# Optionally append the library names preceded by -l
	if args.dash_little_l:
		# Extract the library names from the directory list
		lib_names = [x.split("/")[-1].lower() for x in library_list]

		# Create the library string
		library_string += " -l" + " -l".join(lib_names)

	print(library_string)


def get_lib(libraries, board, boards):
	"""Return a list of directories containing compiled versions of the given libraries.

	The output list is ordered identically to the input list. This preserves
	dependency-related ordering, if there is any.

	This function itself does *not* resolve dependencies.
	"""
	# Set up environment variables for each make instance
	env = {lib: {"LIBRARY": lib} for lib in libraries}

	# Set up a dictionary of make processes
	makes = {}

	# Set up a dictionary of compilation directories
	compile_dirs = {lib: os.path.join(config["compile_root"], board, lib) for lib in libraries}

	# Set up common arguments
	cflags = get_cflags(board, boards)
	variant = boards[board]["build.variant"]
	all_src = get_src(libraries, variant)

	for lib in env:
		# No need to make the math library
		if lib == math_library:
			continue

		# Set common variables
		env[lib]["BOARD"] = board
		env[lib]["BOARD_C_FLAGS"] = cflags
		env[lib]["PATH"] = os.environ["PATH"]

		# Set library specific variables
		lib_src = get_src([lib], variant)
		lib_obj = get_obj(lib_src)

		# XXX: Bit hackish; include all src directories when building...
		env[lib]["SRC_DIRS"] = " ".join(all_src)
		env[lib]["INCLUDES"] = "-I" + " -I ".join(all_src)
		env[lib]["LIBOBJS"] = " ".join(lib_obj)

		# Set the compilation directory
		compile_dir = compile_dirs[lib]
		try:
			os.makedirs(compile_dir, mode = 0o0775, exist_ok = True)
		except OSError:
			pass

		# Find the makefile to use
		specialised_makefile = "makefiles/libraries/{:s}.mk".format(lib)
		if pkg.resource_exists(__name__, specialised_makefile):
			makefile = pkg.resource_filename(__name__, specialised_makefile)
		else:
			makefile = pkg.resource_filename(__name__, "makefiles/Library.mk")

		# Run make in a subprocess
		make_args = ["make", "-f", makefile]
		makes[lib] = subprocess.Popen(make_args, cwd = compile_dir, env = env[lib],
						stdout = subprocess.PIPE, stderr = subprocess.PIPE)

	# Wait for make processes to finish and collect output
	error = False
	output = {}
	for lib in makes:
		returncode = makes[lib].wait()
		stdout, stderr = makes[lib].communicate()
		output[lib] = stdout.decode()

		if returncode != 0:
			error = True
			output[lib] += stderr.decode()

	if error:
		for lib in output:
			print("-- Output from %s make command --" % lib)
			print(output[lib])
		_error("Fatal error, unable to compile all libraries.")

	library_list = [compile_dirs[lib] for lib in libraries]
	return (library_list, output)


def make(args = "unused"):
	"""Make the project in the current directory, using its Makefile.

	This function "pre-fills" all xuino variables to avoid multiple calls and
	provides more helpful diagnostic output than a plain `make`.

	If you've altered your makefile drastically this isn't guaranteed to work.
	"""
	# Check for makefile existence
	if not os.path.isfile("Makefile"):
		m = "No Makefile in the current directory.\n" \
			"Run `xuino init` to get one."
		_error(m)

	# Attempt to get the BOARD & LIBRARIES variables from the shell environment
	board = None
	libraries = None
	if "BOARD" in os.environ:
		board = os.environ["BOARD"]
	if "LIBRARIES" in os.environ:
		libraries = os.environ["LIBRARIES"]

	# Otherwise read them from the makefile
	makefile = None
	if board is None or libraries is None:
		makefile = open("Makefile", "r")
		board_regex = re.compile(r"^BOARD\s*=(?P<value>[^#]*).*$")
		lib_regex = re.compile(r"^LIBRARIES\s*=(?P<value>[^#]*).*$")

	while board is None or libraries is None:
		line = makefile.readline()
		if line == "":
			_error("Unable to extract BOARDS & LIBRARIES from Makefile.")

		if board is None:
			match = board_regex.match(line)
			if match:
				board = match.group("value").strip()

		if libraries is None:
			match = lib_regex.match(line)
			if match:
				libraries = match.group("value").strip()

	if makefile is not None:
		makefile.close()

	# Read boards.txt
	boards = read_boards()

	# Check that the board is valid
	if board not in boards:
		_error("Board not found '{}'".format(board))

	# Turn libraries into a list
	libraries = libraries.split(" ")

	# If libraries is empty, make it the empty list
	if libraries == [""]:
		libraries = []

	# Resolve dependencies
	libraries = resolve_dependencies(libraries)


	# Get the compiler flags
	cflags = get_cflags(board, boards)

	# Get the source directories & header includes
	variant = boards[board]["build.variant"]
	src_dirs = get_src(libraries, variant)
	header_includes = "-I " + " -I ".join(src_dirs)
	src_dirs = " ".join(src_dirs)

	# Make the libraries
	print("Making libraries...")
	lib_dirs, output = get_lib(libraries, board, boards)

	# Print make output, so the user knows what's going on
	for lib in output:
		print("-- Output from %s make command --" % lib)
		print(output[lib])

	# Create the full library include string
	lib_includes = " -L " + " -L ".join(lib_dirs)
	lib_names = [x.split("/")[-1].lower() for x in lib_dirs]
	lib_includes += " -l" + " -l".join(lib_names)

	# Make the actual project
	env = { "BOARD_C_FLAGS": cflags,
		"SRC_DIRS": src_dirs,
		"HEADER_INCLUDES": header_includes,
		"LIB_INCLUDES": lib_includes,
		"PATH": os.environ["PATH"]
	}
	# XXX: Should we pass all of os.environ?

	make = subprocess.Popen(["make"], env = env)
	returncode = make.wait()
	if returncode == 0:
		print("Success!")
	else:
		_error("Oh no! Make failed :(")


def _setup_argparser():
	"""Create the command-line argument parser for Xuino."""
	# Subclass the standard argument parser to provide more helpful error messages
	class ArgumentParser(argparse.ArgumentParser):
		def error(self, message):
			self.print_help()
			print("\nError: %s" % message)
			sys.exit(1)

	# Top level parser
	parser = ArgumentParser(prog = "xuino")
	subparsers = parser.add_subparsers()

	# Help strings
	h_init = "Create a new Arduino project."
	h_init_dir = "The directory in which to create the new project."
	h_clean = "Clear out the cache of compiled library code."
	h_list = "List all available boards."
	h_make = "Make the project in the current directory (verbosely)."
	h_get = "Get compiler flags, compiled libraries, etc."
	h_gprop1 = "Get a board property from boards.txt"
	h_gprop2 = "The name of the property as it appears in boards.txt\n" \
				"E.g. atmega328.build.f_cpu"
	h_board = "The short name of your Arduino board.\n" \
				"Run `xuino list` for a list."
	h_cflags = "Get the compiler flags for a specific board."
	h_src = "Get a list of directories containing library source code."
	h_src_libs = "A list of libraries to get source directories for."
	h_dash_i = "Add a -I before each directory (see gcc's -I option)."

	h_obj = "Get the names of all the .o files for a library."
	h_obj_lib = "The name of the library."

	h_lib = "Get the location(s) of compiled libraries"
	h_lib_libs = "A list of libraries to obtain compiled version of."
	h_dash_big_l = "Add a -L before each directory (see gcc's -L option)."
	h_dash_little_l = "Add a list of compiled archive names beginning with -l\n"\
						"For example: -lethernet -lspi -lcore"

	# Parser for `xuino init`
	init_parser = subparsers.add_parser("init", help = h_init)
	init_parser.add_argument("dir", nargs = "?", default = ".", help = h_init_dir)
	init_parser.set_defaults(func = _init)

	# Parser for `xuino clean`
	clean_parser = subparsers.add_parser("clean", help = h_clean)
	clean_parser.set_defaults(func = _clean)

	# Parser for `xuino list`
	list_parser = subparsers.add_parser("list", help = h_list)
	list_parser.set_defaults(func = _list_boards)

	# Parser for `xuino make`
	make_parser = subparsers.add_parser("make", help = h_make)
	make_parser.set_defaults(func = make)

	# Parser for `xuino get`
	get_parser = subparsers.add_parser("get", help = h_get)
	get_subparsers = get_parser.add_subparsers()

	# Parser for `xuino get property`
	property_parser = get_subparsers.add_parser("property", help = h_gprop1)
	property_parser.add_argument("property", help = h_gprop2)
	property_parser.set_defaults(func = _get_property)

	# Parser for `xuino get cflags`
	cflags_parser = get_subparsers.add_parser("cflags", help = h_cflags)
	cflags_parser.add_argument("board", help = h_board)
	cflags_parser.set_defaults(func = _get_cflags)

	# Parser for `xuino get src`
	src_parser = get_subparsers.add_parser("src", help = h_src)
	src_parser.add_argument("libraries", nargs = "*", help = h_src_libs)
	src_parser.add_argument("--board", default = None, help = h_board)
	src_parser.add_argument("-I", dest = "dash_i", action = "store_true", help = h_dash_i)
	src_parser.set_defaults(func = _get_src)

	# Parser for `xuino get obj`
	obj_parser = get_subparsers.add_parser("obj", help = h_obj)
	obj_parser.add_argument("library", help = h_obj_lib)
	obj_parser.set_defaults(func = _get_obj)

	# Parser for `xuino get lib`
	lib_parser = get_subparsers.add_parser("lib", help = h_lib)
	lib_parser.add_argument("libraries", nargs = "*", help = h_lib_libs)
	lib_parser.add_argument("--board", required = True, help = h_board)
	lib_parser.add_argument("-L", dest = "dash_big_l", action = "store_true", help = h_dash_big_l)
	lib_parser.add_argument("-l", dest = "dash_little_l", action = "store_true",
								help = h_dash_little_l)
	lib_parser.add_argument("-v", "--verbose", action = "store_true")
	lib_parser.set_defaults(func = _get_lib)

	return parser


# Config initialised here upon importing
config = read_config()


# Main function, entry point
def main():
	# Set the 'standalone' flag so neat errors are printed rather than stacktraces
	global running_standalone
	running_standalone = True

	# Parse args
	parser = _setup_argparser()
	args = parser.parse_args()

	# If no command has been given, bail out
	if not hasattr(args, "func"):
		parser.print_help()
		sys.exit(1)

	# Otherwise, execute the command
	args.func(args)

# vim: set noexpandtab tabstop=4 :
# Local variables:
# tab-width: 4
# indent-tabs-mode: 4
# End:
