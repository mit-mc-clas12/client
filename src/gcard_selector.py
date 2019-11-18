#!/usr/bin/env python
# ****************************************************************
"""
# Info
"""
# ****************************************************************

from __future__ import print_function
from utils import (fs, gcard_helper, get_args, scard_helper,
                   user_validation, utils)
import argparse
import os
import sqlite3
import subprocess
import sys
import time
import numpy as np
from subprocess import PIPE, Popen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../../')


def selector(options):
    print("\n Select a gcard by number (1-{0}) from the above list: ".format(
        len(options)-1))
    selection = input()
    return selection


def select_gcard(args):
    filename = fs.dirname+"/valid_gcards.txt"
    with open(filename) as f:
        content = f.readlines()
        content = [x.strip("\n") for x in content]

    for linenum, line in enumerate(content):
        if not linenum == 0:
            print("({0}) - {1}".format(linenum, line))

        else:
            print(line+"\n")

    selection = selector(content)

    while (selection not in np.arange(1, len(content))
           or not (isinstance(selection, int))):
        print(("\n Selection not in valid range, try again, or "
               "hit ctrl+c to exit"))
        selection = selector(content)
        gcard_selected = content[selection].split(',')[0]

    print("Gcard for simultions will be {0}".format(gcard_selected))

    return gcard_selected


if __name__ == "__main__":
    args = get_args.get_args()
    select_gcard(args)
