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
    
    To Do: 
    ------
    -> Move some SQL statements to another package (bottom)
    -> Ensure support for sqlite still works
    """

    logger = utils.configure_logger(args)

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
    logger.debug(
        'Found {}@{} at time: {}'.format(username, domain_name, 
                                         timestamp))

    # A simple name based method for retrieval 
    # of the scard type.  Open the SCard to validate 
    # this submission before starting the database 
    # population. 
    scard_fields = scard_handler.open_scard(args.scard)
    scard_type = scard_handler.get_scard_type(args.scard)
    logger.debug('Type inference for SCard: {}'.format(scard_type))

    # Add the gcard name to the database, we should probably
    # check first that the gcard exists in the container.
    if scard_type in [1, 2]:
        
        if scard_fields.data['gcards'] in fs.container_gcards:
            logger.debug('Adding (type 1/2) gcard: {}'.format(
                scard_fields.data['gcards']))
        else:
            exep = ("The supplied gcard: {0} is supposed to exist in "
                    "the container, but it was not found.").format(
                        scard_fields.data['gcards']
                    )

            # Consider raising custom exceptions
            raise ValueError(exep)

    elif scard_type in [3, 4]:
        logger.debug('Downloading gcards from {}'.format(
            scard_fields.data['gcards']))
        gcards = gcard_helper.download_gcards(scard_fields.data['gcards'])

        if len(gcards) == 0:
            print('No gcards downloaded from: {0}'.format(
                scard_fields.data['gcards']
            ))
            exit() 

    # From here down, the options have been validated and the 
    # database will be populated. 
    # 
    # If this user is not in our users database, add them.
    if username not in database.get_users(sql):
        logger.debug('Adding new user {} to users'.format(username))
        update_tables.add_new_user(username, domain_name, db_conn, sql)

    # Setup an entry in the UserSubmisisons table for the current submission. 
    user_submission_id = update_tables.add_entry_to_user_submissions(
        timestamp, db_conn, sql)
    logger.debug('UserSubmissionID = {}'.format(user_submission_id))

    # Load the SCard for this submission and inject it into 
    # the database. 
    # 
    update_tables.add_scard_to_user_submissions(scard_fields.raw_text, 
                                                user_submission_id,
                                                db_conn, sql)
    update_tables.add_scard_to_scards_table(scard_fields.data, 
                                            user_submission_id, timestamp, 
                                            db_conn, sql)

    # Add gcard(s) to tables. 
    if scard_type in [1, 2]:
        update_tables.add_gcard_to_gcards_table(scard_fields.data['gcards'], 
                                                user_submission_id, 
                                                db_conn, sql)
    elif scard_type in [3, 4]:
        for gcard in gcards:
            update_tables.add_gcard_to_gcards_table(gcard, user_submission_id, 
                                                    db_conn, sql)


    user_id = database.get_user_id(username, sql)
    logger.debug('For User = {}, UserID = {}'.format(username, user_id))

    # Get identification numbers for the gcards in 
    # this submission.  Then clean them into values
    # from tuples of form: 
    # ((gcard_id1,), (gcard_id2,), ...).
    gcard_ids = [ gcard_id[0] for gcard_id in 
        database.select_by_user_submission_id(
            usub_id=user_submission_id, fields='GcardID', 
            table='Gcards', sql=sql
        )
    ]

    # Update User and UserID for this submission with key  UserSubmissionID
    logger.debug('Updating UserSubmissions(User,UserID) = ({},{})'.format(
        username, user_id
    ))
    update_tables.update_user_information(username, user_id, user_submission_id,
                                          db_conn, sql)

    # Finally, update the FarmSubmissions table 
    for gcard_id in gcard_ids:
        logger.debug('Inserting GcardID {} into table.'.format(gcard_id))
        update_tables.add_entry_to_farm_submissions(
            user_submission_id, gcard_id, 
            scard_fields.data['farm_name'], 
            db_conn, sql
        )

    db_conn.close() 
    
def configure_args():
    """Configure and collect arguments from command line."""

    ap = argparse.ArgumentParser() 

    help_str = ("relative path and name scard you"
                "want to submit, e.g. ../scard.txt")
    ap.add_argument('scard', help=help_str, nargs='?')

    ap.add_argument('-d', '--debug', default=0, type=int)

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

    if args.scard:
        client(args)
    else:
        print("No scard detected. Please call python SubMit.py -h for help.")
