#!/usr/bin/env python
#****************************************************************
"""
# Info
"""
#****************************************************************

from __future__ import print_function
import argparse, os, sqlite3, subprocess, sys, time
import numpy as np
from subprocess import PIPE, Popen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../../')
#Could also do the following, but then python has to search the
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import fs, gcard_helper, get_args, scard_helper, user_validation, utils


def gcard_writer(args):

    print("You have not specified a custom gcard, please use one of the common CLAS12 gcards listed below \n")
    scard_fields.data['gcards'] = gcard_selector.select_gcard(args)
    utils.printer("Writing GCards to Database")
    gcard_helper.GCard_Entry(BatchID,timestamp,scard_fields.data['gcards'])
    print("Successfully added gcards to database")
    strn = "UPDATE Batches SET {0} = '{1}' WHERE BatchID = {2};".format('UserID',userid,BatchID)
    utils.db_write(strn)

    strn = "UPDATE Batches SET {0} = '{1}' WHERE BatchID = {2};".format('User',username,BatchID)
    utils.db_write(strn)


    strn = "SELECT GcardID, gcard_text FROM Gcards WHERE BatchID = {0};".format(BatchID)
    gcards = utils.db_grab(strn)
    for gcard in gcards:
      GcardID = gcard[0]
      strn = "INSERT INTO Submissions(BatchID,GcardID) VALUES ({0},{1});".format(BatchID,GcardID)
      utils.db_write(strn)
      strn = "UPDATE Submissions SET submission_pool = '{0}' WHERE GcardID = '{1}';".format(scard_fields.data['farm_name'],GcardID)
      utils.db_write(strn)
      strn = "UPDATE Submissions SET run_status = 'Not Submitted' WHERE GcardID = '{0}';".format(GcardID)
      utils.db_write(strn)
