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

# Ensure that the client can locate utils.  Having to call sys
# before this import breaks PEP8.  This will be fixed by
# packaging and installing the utilities.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../../')
from utils import (database, fs, gcard_helper, get_args,
                   scard_helper, user_validation, utils)

# This project imports
import gcard_handler
import gcard_selector
import scard_handler
import update_tables


def client(args):
    """
    Main client function.  This is the driver which validates the scard
    submitted and populates the database tables.
    """

    logger = utils.configure_logger(args)

    db_conn, sql = setup_database(args)
    
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

    # Verify that the gcard exists in our container, try to
    # download online gcards for types 3/4.  If any of this
    # fails we do not go forward with submission.
    if scard_type in [1, 2]:

        if scard_fields.data['gcards'] in fs.container_gcards:
            logger.debug('Adding (type 1/2) gcard: {}'.format(
                scard_fields.data['gcards']))
        else:
            exep = ("The supplied gcard: {0} is supposed to exist in "
                    "the container, but it was not found.").format(
                        scard_fields.data['gcards']
                    )

            logger.error(exep)
            exit()

    elif scard_type in [3, 4]:
        logger.info('Types 3/4 are not supported yet!')

    """
    -----------------------------------------------
    From this point and down, all options have been
    validated and the databases will be populated.
    -----------------------------------------------
    """

    if username not in database.get_users(sql):
        logger.debug('Adding new user {} to users'.format(username))
        update_tables.add_new_user(username, domain_name, db_conn, sql)

    # Setup an entry in the UserSubmissions table for the current submission.
    user_submission_id = update_tables.add_entry_to_user_submissions(
        timestamp, db_conn, sql)
    logger.debug('user_submission_id = {}'.format(user_submission_id))

    # Update database tables with scard
    update_tables.add_scard_to_submissions(scard_fields.raw_text,
                                                user_submission_id,
                                                db_conn, sql)

    user_id = database.get_user_id(username, sql)
    logger.debug('For user = {}, user_id = {}'.format(username, user_id))

    # Update User and UserID for this submission with key  UserSubmissionID
    logger.debug('Updating submissions(user,user_id) = ({},{})'.format(
        username, user_id
    ))
    update_tables.update_user_information(username, user_id,
                                          user_submission_id,
                                          db_conn, sql)

    update_tables.add_entry_to_submissions(
        user_submission_id, 
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

    help_str = ("use -l=<database> or --lite=<database> to connect to"
                " an sqlite database.")
    ap.add_argument('-l', '--lite', help=help_str, required=False,
                    type=str, default=None)

    help_str = ("Enter user ID for web-interface,"
                "Only if \'whoami\' is \'gemc\'")
    ap.add_argument('-u', '--username', default=None, help=help_str)

    help_str = ("Passing this arguement will instruct"
                "the client to connect to MySQL:CLAS12TEST"
                "database, instead of CLAS12OCR (production)")
    ap.add_argument('--test_database', default=False, help=help_str,
                    action='store_true')
    
    # Collect args from the command line and return to user
    return ap.parse_args()

def setup_database(args):
    """ Configure and open the database connection
    based on user settings. 

    Inputs: 
    -------
    - args - argparse args for setting up the 
    database connection.
    """
    cred_file = os.path.dirname(os.path.abspath(__file__)) + \
                '/../../msqlrw.txt'
    cred_file = os.path.normpath(cred_file)
    username, password = database.load_database_credentials(cred_file)

    if args.lite is not None:
        database_name = args.lite 
    else:
        if args.test_database:
            database_name = "CLAS12TEST"
        else:
            database_name = "CLAS12OCR"

    use_mysql = False if args.lite else True
    db_conn, sql = database.get_database_connection(
        use_mysql=use_mysql,
        database_name=database_name,
        username=username,
        password=password,
        hostname='jsubmit.jlab.org'
    )
    return db_conn, sql

if __name__ == "__main__":

    args = configure_args()
    if args.scard:
        client(args)
    else:
        print("No scard detected. Please call python SubMit.py -h for help.")
