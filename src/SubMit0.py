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
import gcard_selector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../../')
#Could also do the following, but then python has to search the
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import fs, gcard_helper, get_args, scard_helper, user_validation, utils

def User_Submission(args):
    timestamp = utils.gettime() # Can modify this if need 10ths of seconds or more resolution
    strn = """INSERT INTO Batches(timestamp) VALUES ("{0}");""".format(timestamp)
    BatchID = utils.db_write(strn)
    scard_file = args.scard

    #Write the text contained in scard.txt to a field in the Batches table
    with open(scard_file, 'r') as file: scard = file.read()
    strn = """UPDATE Batches SET {0} = '{1}' WHERE BatchID = "{2}";""".format('scard',scard,BatchID)
    utils.db_write(strn)
    utils.printer("Batch specifications written to database with BatchID {0}".format(BatchID))

    #See if user exists already in database; if not, add them
    with open(scard_file, 'r') as file: scard_text = file.read()
    scard_fields = scard_helper.scard_class(scard_text)
    username = user_validation.user_validation()

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


    strn = "SELECT UserID FROM Users WHERE User = '{0}';".format(username)
    userid = utils.db_grab(strn)[0][0]


    #Write gcards into gcards table
    gcard_writer.gcard_writer(args)

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
