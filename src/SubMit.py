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
from utils import (database, fs, gcard_helper, get_args, 
                   scard_helper, user_validation, utils)


def run_client(args):
    """This is the original client function."""
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

def client(args):
    """ Client that depends on the database explicitly.
    
    1) Get database connection setup 
    2) Determine the username, provided usernames at the CL 
       take priority over inferred usernames. 
    3) If this is a new user, add them to our 
       users database.  Then setup a submission ID 
       for this submission. 
    4) Inject the SCard into our databases

    """

    # Setup database connection.
    update_fs_from_args(args)
    update_database_authentication(args)
    db_conn, sql = database.get_database_connection() 

    # Get basic information related to this user submission. 
    # If the username is provided at the CL, that takes 
    # priority over inference of the username. 
    timestamp = utils.gettime() 
    username = args.username or user_validation.get_username()
    domain_name = user_validation.get_domain_name()

    # If this user is not in our users database, add them.
    if username not in database.get_users(sql):
        update_tables.add_new_user(username, domain_name, sql)

    # Setup an entry in the UserSubmisisons table for the current submission. 
    user_submission_id = update_tables.add_entry_to_user_submissions(
        timestamp, sql)

    # Load the SCard for this submission and inject it into 
    # the database. 
    scard_fields = scard_handler.open_scard(args.scard)
    update_tables.add_scard_to_user_submissions(scard_fields, 
                                                user_submission_id,
                                                timestamp, sql)
    update_tables.add_scard_to_scards_table(scard_fields.data, 
                                            user_submission_id, sql)

    # A simple name based method for retrieval 
    # of the scard type.
    scard_type = scard_handler.get_scard_type(args.scard)

    # Add the gcard name to the database, we should probably
    # check first that the gcard exists in the container.
    if scard_type in [1, 2]:
        
        if scard_fields.data['gcards'] in fs.container_gcards:
            update_tables.add_gcard_to_gcards_table(scard_fields.data['gcards'], 
                                                    user_submission_id, sql)
        else:
            exep = ("The supplied gcard: {0} is supposed to exist in "
                    "the container, but it was not found.").format(
                        scard_fields.data['gcards']
                    )
            # Consider raising custom exceptions, I don't think 
            # ValueError is really appropriate.
            raise ValueError(exep)

    # Go through the exercise of downloading the 
    # gcard(s) and adding them to the database.
    #
    # Is there a better way than explicitly checking 
    # type here? 
    elif scard_type in [3, 4]:

        # I still need to write this function, which is already in 
        # existence in GCard_Entry()
        gcards = gcard_helper.download_gcards(scard_fields.data['gcards'])

        # Add a call before this to make sure that something was found
        # and if not, alert the user and stop the submission.  Perhaps 
        # this should even be done before the start of injection of
        # anything in the database so that we don't end up with partial 
        # submissions in our database getting passed off to the server?
        for gcard in gcards:
            update_tables.add_gcard_to_gcards_table(gcard, user_submission_id, sql)

    # gcard_handler (ignore my notes - sorry)
    """ 
    Look at the string provided for the gcards: entry 
    in the scard.  Two possible cases exist (the) current 
    code tries to handle a third case, but I don't think 
    there are three cases.

    First case: Type 1/2 scard, where the gcard specified 
    exists in the container.

    Second case: Type 3/4 scard, where the gcard(s) are 
    included from the web.

    How do we want to handle the inference of scard type? 
    - It should be done once, that's all.
    - It can be done a few ways: 
        - (a) Look at the scard title, this should contain the simple 
              designation typeX, where X is the type number.  This is 
              not a robust solution, but if the scard is only ever 
              produced automatically by the web interface, it will work 
              just fine.
        - (b) Infer the type from the fields within the scard, this can 
              be done.  The functionality already exists in the codebase.
              That code is currently on the server side, in type_manager.py 
    """

    # Update tables (ignore my notes - sorry)
    """ 
    Find the UserID for this submission and pull down the 
    GcardID and gcard_text that was injected into the database
    in the previous step.

    Then, update the UserSubmissions table with the current UserID 
    and User for the current UserSubmissionID.

    For each gcard found in the first step: 
        (a) Create an entry in the FarmSubmissions table with the 
            UserSubmissionID and GcardID 
        (b) Add the farm name to FarmSubmissions 
        (c) Set FarmSubmissions.run_status to Not Submitted (this 
            ensures that the server picks up the submission).
    """

    user_id = database.get_user_id(username, sql)

    # This could return more than one I guess, if there 
    # were multiple cards downloaded and inserted into 
    # the database. 
    gcard_id = database.select_by_user_submission_id(
        usub_id=user_submission_id, fields='GcardID', 
        table='Gcards', sql=sql
    )

    # Above, we could have selected the gcard_id and gcard_text 
    # from the Gcards table.  We already have the gcards here in 
    # the gcards variable, but now the problem is ensuring that 
    # they stay synchronized (it should be).

    # Move this to a function in the update tables 
    # module. 
    update_template = """
        UPDATE UserSubmissions SET {0} = '{1}'
            WHERE UserSubmissionID = {2};
        """
    sql.execute(update_template.format('UserID', user_id, user_submission_id))
    sql.execute(update_template.format('User', username, user_submission_id))

    # Finally, update the FarmSubmissions table 
    update_tables.add_entry_to_farm_submissions(
        user_submission_id, gcard_id, 
        scard_fields.data['farm_name'], sql
    )

    db_conn.close() 
    

def configure_args():
    """Configure and collect arguments from command line."""

    ap = argparse.ArgumentParser() 

    help_str = ("relative path and name scard you"
                "want to submit, e.g. ../scard.txt")
    ap.add_argument('scard', help=help_str, nargs='?')

    ap.add_argument(fs.debug_short, fs.debug_longdash, 
        default=fs.debug_default, help=fs.debug_help
    )

    help_str = ("use -l or --lite to connect to"
                "sqlite DB, otherwise use MySQL DB")
    ap.add_argument('-l', '--lite', help=help_str, action='store_true')

    help_str = ("Enter user ID for web-interface," 
                "Only if \'whoami\' is \'gemc\'")
    ap.add_argument('-u', '--username', default=None, help=help_str)
    
    # Collect args from the command line and return to user
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
