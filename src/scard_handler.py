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


def scard_handler(args,BatchID,timestamp):
  scard_file = args.scard

  #Write the text contained in scard.txt to a field in the Batches table
  with open(scard_file, 'r') as file: scard = file.read()
  strn = """UPDATE Batches SET {0} = '{1}' WHERE BatchID = "{2}";""".format('scard',scard,BatchID)
  utils.db_write(strn)
  utils.printer("Batch specifications written to database with BatchID {0}".format(BatchID))

  #See if user exists already in database; if not, add them
  with open(scard_file, 'r') as file: scard_text = file.read()
  scard_fields = scard_helper.scard_class(scard_text)

  #Write scard into scard table fields (This will not be needed in the future)
  print("\nReading in information from {0}".format(scard_file))
  utils.printer("Writing SCard to Database")
  scard_fields.data['group_name'] = scard_fields.data.pop('group') #'group' is a protected word in SQL so we can't use the field title "group"
  # For more information on protected words in SQL, see https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=RSQL_reservedwords

  if 'http' in scard_fields.data.get('generator'):
    print("Online repository for generator files specified. On server will download LUND files from:")
    print("{0}".format(scard_fields.data.get('generator')))
    scard_fields.data['genExecutable'] = "Null"
    scard_fields.data['genOutput']     = "Null"
    scard_fields.data['genOptions']    = "Null"
    scard_fields.data['nevents']       = "User Lund File Driven"
    scard_fields.data['jobs']          = "One per User Lund File"
  else:
    scard_fields.data['genExecutable'] = fs.genExecutable.get(scard_fields.data.get('generator'))
    scard_fields.data['genOutput']     = fs.genOutput.get(scard_fields.data.get('generator'))

  scard_helper.SCard_Entry(BatchID,timestamp,scard_fields.data)
  print('\t Your scard has been read into the database with BatchID = {0} at {1} \n'.format(BatchID,timestamp))

  return scard_fields

if __name__ == "__main__":
  args = get_args.get_args_client()
  scard_handler(args,BatchID,timestamp)
