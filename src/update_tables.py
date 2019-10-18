#!/usr/bin/env python

""" 

This module contains client side utilities for updating 
the main SQL tables.  Anything that uses INSERT or UPDATE 
lives here.  

"""


from __future__ import print_function
import argparse, os, sqlite3, subprocess, sys, time
import numpy as np
from subprocess import PIPE, Popen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../../')
# Could also do the following, but then python has to search the
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import fs, gcard_helper, get_args, scard_helper, user_validation, utils

def update_tables(args, UserSubmissionID, username, timestamp, scard_fields):
    # Grab username and gcard information that just got entered into DB
    strn = "SELECT UserID FROM Users WHERE User = '{0}';".format(username)
    userid = utils.db_grab(strn)[0][0]
    strn = "SELECT GcardID, gcard_text FROM Gcards WHERE UserSubmissionID = {0};".format(UserSubmissionID)
    gcards = utils.db_grab(strn)

    # Update tables
    strn = "UPDATE UserSubmissions SET {0} = '{1}' WHERE UserSubmissionID = {2};".format('UserID',userid,UserSubmissionID)
    utils.db_write(strn)
    strn = "UPDATE UserSubmissions SET {0} = '{1}' WHERE UserSubmissionID = {2};".format('User',username,UserSubmissionID)
    utils.db_write(strn)
    for gcard in gcards:
      GcardID = gcard[0]
      strn = "INSERT INTO FarmSubmissions(UserSubmissionID,GcardID) VALUES ({0},{1});".format(UserSubmissionID, GcardID)
      utils.db_write(strn)
      strn = "UPDATE FarmSubmissions SET submission_pool = '{0}' WHERE GcardID = '{1}';".format(scard_fields.data['farm_name'],GcardID)
      utils.db_write(strn)
      strn = "UPDATE FarmSubmissions SET run_status = 'Not Submitted' WHERE GcardID = '{0}';".format(GcardID)
      utils.db_write(strn)

if __name__ == "__main__":
  args = get_args.get_args_client()
  update_tables(args, UserSubmissionID, username,scard)

def add_new_user(username, domain_name, sql):
    """Add a user to the Users table."""
    
    strn = """ 
    INSERT INTO Users(
        User, domain_name, JoinDateStamp, Total_UserSubmissions,
        Total_Jobs, Total_Events, Most_Recent_Active_Date
    )
    VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}"); 
    """.format(username, domain_name, utils.gettime(), 0, 0, 0, "Null")
    
    sql.execute(strn)
    
def add_entry_to_user_submissions(timestamp, sql):
    """ Add a new entry to the UserSubmission table, 
    this will auto-increment and assign a UserSubmissionID. """

    strn = """                                                                 
    INSERT INTO UserSubmissions(timestamp)                                     
        VALUES ("{0}");""".format(timestamp)
    
    sql.execute(strn)

    # The last row ID is the assigned UserSubmissionID 
    # for this submission. 
    return sql.lastrowid 

def inject_scard(scard, user_submission_id, sql):
  """Inject the scard raw into the table UserSubmissions """
  strn  = """                                                               
  UPDATE UserSubmissions SET {0} = '{1}'                                       
      WHERE UserSubmissionID = "{2}";                                          
  """.format('scard', scard, user_submission_id)
  sql.execute(strn)
