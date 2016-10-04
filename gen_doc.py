#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import os
import re


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

def parse_platform(chibios_path, platform_filename):
    """
    Parse platform.mk file, and find every occurence of C and headers files.
    """
    with open(platform_filename, "r") as f:
        content = f.read()

    # Look for all occurrence of $(CHIBIOS)...*.c
    exp = "(\$(?:\(CHIBIOS\)|{CHIBIOS})\/[\/\w\s]*\.c)"
    C_files = re.findall(exp, content, re.M)

    # Look for all occurrence of $(CHIBIOS)...*.h
    exp = "(\$(?:\(CHIBIOS\)|{CHIBIOS})\/[\/\w\s]*\.h)"
    H_files = re.findall(exp, content, re.M)

    # Look for all occurrence of $(CHIBIOS)...*.s
    exp = "(\$(?:\(CHIBIOS\)|{CHIBIOS})\/[\/\w\s]*\.s)"
    S_files = re.findall(exp, content, re.M)

    # Look for include directories
    exp = "(\$(?:\(CHIBIOS\)|{CHIBIOS})\/[\/\w\s]*)[\s|\n]"
    dir_files = re.findall(exp, content, re.M)

    files = []
    for f in C_files + H_files + S_files + dir_files:
        files.append(replace_CHIBIOS(chibios_path, f))

    return files

def generate_doxyfile_html(files):
    """
    Take the Doxyfile_html template, and replace $(INPUT)
    with the list of files / directory to be parsed.
    """
    with open("Doxyfile_html.template", "r") as f:
        content = f.read()

    file_list = " \\\n                         ".join(files)
    content = content.replace("$(INPUT)",file_list)

    with open("Doxyfile_html", "w") as f:
        f.write(content)



def usage():
    """
    Print a helper message.
    """
    print("Usage:", sys.argv[0], "path_to_your_main_Makefile")
    print("This utility parses the main Makefile of your project, extract the", \
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
