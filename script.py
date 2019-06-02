#!/usr/bin/python
import os
import sys
import subprocess
import time

from numpy import pi

# 0. General Settings
map_count       = 0
number_of_tests = 50


# 1. Defining the experiment type
# 2. Starting the experiment
test_number = 0
while test_number < number_of_tests:
    for maps in range(0,5):
        # a. printing test information
        print '- STARTING TEST ',test_number,' -'
        print '| Map Number: ',maps
        print '---------'

        # b. writing the command
        experiment_run = 'python main.py '+ str(maps)
        print experiment_run

        # c. running it
        os.system(experiment_run)
        time.sleep(5)

        test_number += 1
