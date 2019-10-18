#!/usr/bin/env python
#****************************************************************
"""
# Info
"""
#****************************************************************

from __future__ import print_function
import argparse, os, sqlite3, subprocess, sys, time
import numpy as np
import gcard_selector
from subprocess import PIPE, Popen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../../')
#Could also do the following, but then python has to search the
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import fs, gcard_helper, get_args, scard_helper, user_validation, utils


def gcard_handler(args, UserSubmissionID, timestamp, scard_fields):
    #The below two lines are commented out because we are not currently using interactive gcard selection
    #print("You have not specified a custom gcard, please use one of the common CLAS12 gcards listed below \n")
    #scard_fields.data['gcards'] = gcard_selector.select_gcard(args)

    utils.printer("Writing GCards to Database")
    gcard_helper.GCard_Entry(UserSubmissionID, timestamp, 
                             scard_fields.data['gcards'])
    print("Successfully added gcards to database")

    return scard_fields

if __name__ == "__main__":
  args = get_args.get_args_client()
  gcard_handler(args,UserSubmissionID,timestamp,scard_fields)
