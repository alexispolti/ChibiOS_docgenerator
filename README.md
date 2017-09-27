ChibiOS_docgenerator
=========

A tool to generate the full ChibiOS 4.x and 5.x HAL documentation for your processor.

Copyright 2016 Alexis Polti

Licensed under the GPL v3.0

Maintainer
----------

  * Alexis Polti   <alexis@polti.name>

Requirements
------------

Python3 (sorry, didn't have time to port it on Python2).

Goal
------

The 4.x and 5.x branches of ChibiOS contain only the main HAL's documentation: the documentation of the ports have been supressed, as they are quite difficult to generate. Here's a tool to generate this documentation.

Installation and usage
-----------------------------

- put  ```gen_doc.py``` in ```$(CHIBIOS)/doc/hal```.
- run  ```python3 gen_doc.py Makefile```, passing as argument the full path to the Makefile of your project.

Your ```Makefile``` is parsed, the correct platform is extracted from it and a proper ```Doxyfile_html``` is generated.
You can now either run ```doxygen Doxyfile_html``` or follow the instructions in ```readme.txt```

Caveat
---------

This tools is still crude, and assume that:

- your Makefile contains one and only one line specifying where ChibiOS is located as in the demos: ```CHIBIOS = ...```. It accepts some variations, such as ```CHIBIOS := ...``` and ```CHIBIOS ?= ...```
- your Makefile contains one and only one line specifying your platform of the form ```include $(CHIBIOS)/os/hal/ports/STM32/STM32F4xx/platform.mk```
- this tool doesn't accept (yet) spaces in your project / ChibiOS installation path.
