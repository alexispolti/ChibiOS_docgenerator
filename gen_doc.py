#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import os
import re
import itertools

def replace_CHIBIOS(chibios_path, filename):
    """
    Replace every occurrence of $(CHIBIOS) or ${CHIBIOS} in filename
    by the first argument.
    """
    filename = filename.replace("CHIBIOS", chibios_path).replace("$", "")
    filename = filename.replace("(", "").replace(")", "")
    filename = filename.replace("{", "").replace("}", "")
    return filename

def parse_makefile(filename):
    """
    Parse a Makefile and look for the platform.mk file as
    well as the CHIBIOS variable.
    Return $(CHIBIOS) value and platform.mk absolute path.
    """
    # Look for "include ...../platform.mk"
    exp = "^include (.*\/platform.mk)"
    with open(filename, "r") as f:
        content = f.read()
    res = re.findall(exp, content, re.M)

    # Check that there is only one occurrence of platform.mk
    if len(res) == 0:
        print("Error : no platform.mk defined in your Makefile.")
        os.exit(-1)
    if len(res) > 1:
        print("Error : multiple platform.mk defined in your Makefile")
        os.exit(-1)
    platform = res[0]

    # Look for "CHIBIOS = ..."$
    exp = "^CHIBIOS[:\?\s]=\s?(.*)"
    res = re.findall(exp, content, re.M)

    # Check that there is only one occurrence of CHIBIOS definition
    if len(res) == 0:
        print("Error : path to CHIBIOS is not defined in your Makefile.")
        os.exit(-1)
    if len(res) > 1:
        print("Error : multiple definition of CHIBIOS path defined in your Makefile:")
        for r in res:
            print(r, )
        os.exit(-1)
    CHIBIOS = res[0]

    # Purify CHIBIOS and platform.mk path
    CHIBIOS = os.path.abspath(os.path.dirname(filename) + "/" + CHIBIOS)
    platform = os.path.abspath(replace_CHIBIOS(CHIBIOS, platform))
    return CHIBIOS, platform

def filter_out_fallback(files):
    """
    Given a list of files found in an .mk file, if there are a real LLD port and a fallback one,
    then filter out the fallbacks.
    """
    not_fb = list(filter(lambda l: l.find("fallback") == -1, files))
    if len(not_fb) != 0:
        return not_fb
    return files

def parse_platform(chibios_path, platform_filename):
    """
    Parse platform.mk file, and find every occurence of C and headers files.
    """
    with open(platform_filename, "r") as f:
        content = f.read()

    # Look for all occurrence of $(CHIBIOS)...*.c
    exp = "(\$(?:\(CHIBIOS\)|{CHIBIOS})\/[\/\w]*\.c)"
    C_files = re.findall(exp, content, re.M)
    C_files = filter_out_fallback(C_files)

    # Look for all occurrence of $(CHIBIOS)...*.h
    exp = "(\$(?:\(CHIBIOS\)|{CHIBIOS})\/[\/\w]*\.h)"
    H_files = re.findall(exp, content, re.M)
    H_files = filter_out_fallback(H_files)

    # Look for all occurrence of $(CHIBIOS)...*.s
    exp = "(\$(?:\(CHIBIOS\)|{CHIBIOS})\/[\/\w]*\.s)"
    S_files = re.findall(exp, content, re.M)
    S_files = filter_out_fallback(S_files)

    # Look for include directories
    exp = "(\$(?:\(CHIBIOS\)|{CHIBIOS})\/[\/\w]*)[\s|\n]"
    dir_files = re.findall(exp, content, re.M)
    dir_files = filter_out_fallback(dir_files)

    files = []
    for f in C_files + H_files + S_files + dir_files:
        files.append(replace_CHIBIOS(chibios_path, f))

    # Look for all *.mk files and recursively parse them
    exp = "(\$(?:\(CHIBIOS\)|{CHIBIOS})\/[\/\w]*\.mk)"
    mk_files = re.findall(exp, content, re.M)
    for mk_file in mk_files:
        f = parse_platform(chibios_path, replace_CHIBIOS(chibios_path, mk_file))
        files += filter_out_fallback(f)
        
    return files

def generate_doxyfile_html(files):
    """
    Take the Doxyfile_html and replace INPUT tag
    with the list of files / directory to be parsed.
    Automatically add some key directories.
    """
    # Add some mandatory files
    files += ["./src",
                 "../../os/hal/dox",
                 "../../os/hal/src",
                 "../../os/hal/include",
                 "../../os/hal/lib/peripherals/flash",
                 "../../os/hal/lib/peripherals/sensors"]

    # Now parse Doxyfile_html and modify INPUT tag
    with open("Doxyfile_html", "r") as f:
        content = f.readlines()

    prefix = list(itertools.takewhile(lambda l:not l.startswith("INPUT"), content))
    suffix = list(itertools.dropwhile(lambda l:not re.match(r"^\s*$", l), content[len(prefix)+1:]))
    line = "INPUT                  = "
    line += " \\\n                         ".join(files) + "\n"
    middle = [line]

    with open("Doxyfile_html", "w") as f:
        f.write("".join(prefix + middle + suffix))

    print("Doxyfile_html generated.")
    print("You can now run rm -rf html && doxygen Doxyfile_html or follow the instructions in readme.txt")

def usage():
    """
    Print a helper message.
    """
    print("Usage:", sys.argv[0], "path_to_your_main_Makefile")
    print("This utility parses the main Makefile of your project, extracts the", \
    "correct platform, parses it and generate a Doxyfile_html allowing you", \
    "to generate the ChibiOS documentation specific to your processor.")

def main():
    """
    Look for the main Makefile on the command line and parse it
    to generate the correct Doxyfile_html.
    """

    # Check that the Makefile is passed as argument.
    if len(sys.argv) != 2:
        usage()
        exit(-1)

    # Parse Makefile
    CHIBIOS, platform = parse_makefile(sys.argv[1])
    print("CHIBIOS is in %s"%CHIBIOS)
    print("Found platform.mk : %s"%platform)

    # Parse platform.mk file
    files = parse_platform(CHIBIOS, platform)

    # Generate Doxyfile_html
    generate_doxyfile_html(files)



if __name__ == "__main__":
    main()
