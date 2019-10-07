#!/usr/bin/env python
#****************************************************************
"""
# This is the submission script for use on the client side. Takes in an scard.txt file.
# Default file name is "scard.txt" which must be located in running directory, or can be specified
# directly by executing "python SubMit.py /path/to/scard/scard_name.txt. This will query the computer
# for username and domainname information, add to the databse, then reads the scard, downloads any
# gcards or other files from online repositories, and inserts the inforamtion into the database.
# Please note the database must exist for this to work properly. If the database does not exist
# (while we are using SQLite): go to the server side code and generate the database. Consult the
# most recent README for specific directions on accomplishing this.
"""
#****************************************************************

from __future__ import print_function
import argparse, os, sqlite3, subprocess, sys, time
from subprocess import PIPE, Popen
import gcard_selector, scard_handler, gcard_handler, update_tables
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../../')
#Could also do the following, but then python has to search the
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import fs, gcard_helper, get_args, scard_helper, user_validation, utils

def User_Submission(args):
    # Get time UserSubmission was submitted
    timestamp = utils.gettime()
    # Get user and domain information
    username = user_validation.user_validation(args)
    #Enter UserSubmission timestamp into DB, initializing user submission entry
    strn = """INSERT INTO UserSubmissions(timestamp) VALUES ("{0}");""".format(timestamp)
    UserSubmissionID = utils.db_write(strn)

    #Handle scard information
    scard_fields = scard_handler.scard_handler(args,UserSubmissionID,timestamp)

    #Handle gcard information
    scard_fields = gcard_handler.gcard_handler(args,UserSubmissionID,timestamp,scard_fields)

    #Update tables with gcard and scard information
    update_tables.update_tables(args,UserSubmissionID,username,timestamp,scard_fields)


if __name__ == "__main__":
  args = get_args.get_args_client()

  if args.lite:
    if not os.path.isfile(fs.SQLite_DB_path+fs.DB_name):
      print('Could not find SQLite Database File. Are you sure it exists and lives in the proper location? Consult README for help')
      exit()
  elif not """insert some connection to mysql db test""":
    print('Could not connect to MySQL database. Are you sure it exists and lives in the proper location? Consult README for help')
    exit()

  if not args.scard:
    print('SubMit.py requires an scard.txt file to submit a job. You can find an example listed in the documentation')
    print('Proper usage is `SubMit.py <name of scard file>` e.g. `SubMit.py scard.txt`')
    exit()
  else:
    User_Submission(args)
