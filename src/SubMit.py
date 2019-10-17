#!/usr/bin/env python

"""

This is the submission script for use on the client side. 
Takes in an scard.txt file.  Default file name is "scard.txt" 
which must be located in running directory, or can be specified
directly by executing "python SubMit.py /path/to/scard/scard_name.txt. 
This will query the computer for username and domainname information, 
add to the databse, then reads the scard, downloads any gcards or other
files from online repositories, and inserts the inforamtion into the database.

Please note the database must exist for this to work properly. 
If the database does not exist (while we are using SQLite): go 
to the server side code and generate the database. Consult the
most recent README for specific directions on accomplishing this.

"""

# Future imports 
from __future__ import print_function

# Standard library imports
import os 
import sys 
import time
from subprocess import PIPE, Popen

# Third party imports 
import argparse 
import sqlite3 

# This project imports 
import gcard_handler 
import gcard_selector
import scard_handler
import update_tables 


# Ensure that the client can locate utils. 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../../')
from utils import (fs, gcard_helper, get_args, 
                   scard_helper, user_validation, utils)


def run_client(args):
    """Main client function.  I am moving responsibility 
    outside of other module helper functions and into this 
    function so that the flow of the program is more obvious. 

    The current function works, but is under construction. 

    Proposed Flow (psuedocode): 

    # Setup Database 
    cred_file = '../msqlrw.txt'
    username, password = load_database_credentials(cred_file)
    db_conn, sql = establish_database_connection(username, password)
    
    # Get time this submission is marked as 
    timestamp = utils.gettime() 

    # See if the user is new 
    username = user_validation.get_username() 
    domain_name = user_validation.get_domain_name() 

    # If so, add this user to our database of users
    if username not in user_validation.get_users(sql):
        user_validation.add_new_user(username, domain_name, sql)

    # Setup an entry in the UserSubmissions table for the 
    # current submission. 
    user_submission_id = add_entry_to_user_submissions(sql)
    
    # Load the SCard for this submission and inject it into 
    # the database.
    scard_fields = scard_handler.open_scard(args.scard)
    scard_handler.inject_scard(scard_fields, user_submission_id, 
                               timestamp, sql)
    
    # GCard stuff, I haven't looked into that function yet. 
    # 
    

    # Update tables stuff, I haven't looked into that function. 

    # Close database connection 
    db_connection.close() 

    """


    # Get time UserSubmission was submitted
    timestamp = utils.gettime()

    # Get user and domain information
    username = user_validation.user_validation(args)

    # Enter UserSubmission timestamp into DB, 
    # initializing user submission entry
    strn = """
    INSERT INTO UserSubmissions(timestamp) 
        VALUES ("{0}");""".format(timestamp)
    UserSubmissionID = utils.db_write(strn)

    # Handle scard information
    scard_fields = scard_handler.scard_handler(args, UserSubmissionID, 
                                               timestamp)

    # Handle gcard information
    scard_fields = gcard_handler.gcard_handler(args, UserSubmissionID, 
                                               timestamp, scard_fields)

    # Update tables with gcard and scard information
    update_tables.update_tables(args, UserSubmissionID, 
                                username, timestamp, 
                                scard_fields)

def configure_args():
    """Configure and collect arguments from command line."""

    ap = argparse.ArgumentParser() 
    ap.add_argument(
        'scard', 
        help=("relative path and name scard you"
              "want to submit, e.g. ../scard.txt"),
        nargs='?'
    )
    ap.add_argument(
        fs.debug_short, 
        fs.debug_longdash, 
        default=fs.debug_default, 
        help=fs.debug_help
    )
    ap.add_argument(
        '-l', 
        '--lite', 
        help=("use -l or --lite to connect to"
              "sqlite DB, otherwise use MySQL DB"),
        action = 'store_true'
    )
    ap.add_argument(
        '-u',
        '--username', 
        default=None, 
        help=("Enter user ID for web-interface," 
              "Only if \'whoami\' is \'gemc\'")
    )
    
    # Return arguments to user 
    return ap.parse_args()

def update_fs_from_args(args):
    """ Set some filesystem parameters, not sure if 
    this can be changed to something more like a 
    configuration file or function."""
    fs.DEBUG = getattr(args, fs.debug_long)
    fs.use_mysql = not args.lite

def update_database_authentication(args):
    """Temporary function to authenticate while full 
    database authentication is configured. """
    if not args.lite:
        with open(fs.dirname + '/../msqlrw.txt','r') as myfile:
            login = myfile.read().replace('\n', ' ')
            login_params = login.split()
            fs.mysql_uname = login_params[0]
            fs.mysql_psswrd =  login_params[1]

if __name__ == "__main__":

    args = configure_args() 
    update_fs_from_args(args) 
    update_database_authentication(args)

    if args.lite:
        if not os.path.isfile(fs.SQLite_DB_path + fs.DB_name):
            print(("Could not find SQLite Database File. Are you sure"
                   " it exists and lives in the proper location? "
                   "Consult README for help"))
            exit()

    elif not """insert some connection to mysql db test""":
        print(("Could not connect to MySQL database. Are you "
               "sure it exists and lives in the proper location? "
               "Consult README for help"))
        exit()

    if not args.scard:
        print(("SubMit.py requires an scard file to submit a job. "
               "You can find examples in the documentation."))
        print(("Proper usage is `SubMit.py -u <username> <scard>` "
               "e.g. `SubMit.py -u your-jlab-username scard_type1.txt`"))
        exit()

    else:
        run_client(args)
