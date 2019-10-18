B#!/usr/bin/env python
1;95;0c
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
    """ Update tables does the following: 
    
    1) Find the UserID for this User 
    2) Pull the GcardID and the gcard_text down (save in tuple)
    3) Update the UserSubmissions table with the current 
       UserID and User for the current UserSubmissionID
    4) For each gcard from (2)
           (a) Create an entry in the FarmSubmissions table with the 
               UserSubmissionID and GcardID
           (b) Add the farm name to FarmSubmissions
           (c) Set FarmSubmissions.run_status to Not Submitted (this 
               ensures that the server will pick up the submission the
               next time it searches the database for new entries).

    """

    # Grab username and gcard information that just got entered into DB
    strn = "SELECT UserID FROM Users WHERE User = '{0}';".format(username)
    userid = utils.db_grab(strn)[0][0]
    strn = "SELECT GcardID, gcard_text FROM Gcards WHERE UserSubmissionID = {0};".format(UserSubmissionID)
    gcards = utils.db_grab(strn)

    # Update tables
    template = "UPDATE UserSubmissions SET {0} = '{1}' WHERE UserSubmissionID = {2};"
    strn = template.format('UserID', userid, UserSubmissionID)
    utils.db_write(strn)
    strn = template.format('User', username, UserSubmissionID)
    utils.db_write(strn)

    for gcard in gcards:
      GcardID = gcard[0]
      strn = "INSERT INTO FarmSubmissions(UserSubmissionID,GcardID) VALUES ({0},{1});".format(UserSubmissionID, GcardID)
      utils.db_write(strn)
      strn = "UPDATE FarmSubmissions SET submission_pool = '{0}' WHERE GcardID = '{1}';".format(scard_fields.data['farm_name'],GcardID)
      utils.db_write(strn)
      strn = "UPDATE FarmSubmissions SET run_status = 'Not Submitted' WHERE GcardID = '{0}';".format(GcardID)
      utils.db_write(strn)

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

def add_scard_to_user_submissions(scard, user_submission_id, sql):
  """Inject the scard raw into the table UserSubmissions """
  strn  = """                                                               
  UPDATE UserSubmissions SET {0} = '{1}'                                       
      WHERE UserSubmissionID = "{2}";                                          
  """.format('scard', scard, user_submission_id)
  sql.execute(strn)

def add_scard_to_scards_table(scard_fields, usub_id, timestamp, sql):
    """ Add the scard data dictionary to the database table called 
    Scards.  The Scard is also defined in the UserSubmissions database.
    
    Inputs: 
    -------
    scard_fields - dict containing the data (field, value) from the scard
    usub_id - integer UserSubmissionID generated for this submission 
    timestamp - common timestamp for all operations on this submission 

    To Do: 
    ------
    - Add logging 
    - Add test (need in memory sqlite database)
    """

    strn = """
    INSERT INTO Scards(UserSubmissionID,timestamp) 
        VALUES ("{0}","{1}");
    """.format(usub_id, timestamp)
    sql.execute(strn)

    update_template = """
    UPDATE Scards SET {0} = '{1}' 
        WHERE UserSubmissionID = {2}
    """
    for field, field_value in scard_fields.items():
      sql.execute(update_template.format(field, field_value, usub_id))

def add_gcard_to_gcards_table(gcard_text, usub_id, sql):
    """ Create an entry in the Gcards table for this user
    submission and then write the Gcard text into it. 

    Inputs:
    ------
    gcard_text - the text of the gcard file
    usub_id - UserSubmissionID from the UserSubmissions table for this submission
    sql - The database cursor object for writing.

    """

    strn = """
    INSERT INTO Gcards(UserSubmissionID)
        VALUES ({0});
    """.format(usub_id)
    sql.execute(strn)

    strn = """
    UPDATE Gcards SET {0} = "{1}"
        WHERE UserSubmissionID = {2};
    """.format(gcard_text, usub_id)
    sql.execute(strn)

def add_entry_to_farm_submissions(usub_id, gcard_id, farm_name, sql):
    """ Create an entry in the FarmSubmissions table for this 
    user submission.  

    Inputs:
    -------
    usub_id - UserSubmissionID for this submission (int)
    gcard_id - GcardID for this submission (int)
    farm_name - Name of farm destination (str)
    sql - The database cursor object for writing. 

    """
    strn = """
    INSERT INTO FarmSubmissions(UserSubmissionID,GcardID) 
        VALUES ({0},{1});
    """.format(usub_id, gcard_id)
    sql.execute(strn)

    strn = """
    UPDATE FarmSubmissions SET submission_pool = '{0}' 
        WHERE GcardID = '{1}';
    """.format(farm_name, gcard_id)
    sql.execute(strn)

    strn = """
    UPDATE FarmSubmissions SET run_status = 'Not Submitted' 
        WHERE GcardID = '{0}';
    """.format(gcard_id)
    sql.execute(strn)
