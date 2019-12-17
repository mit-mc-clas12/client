#!/usr/bin/env python

"""

This module contains client side utilities for updating
the main SQL tables.  Anything that uses INSERT or UPDATE
lives here.

"""


from __future__ import print_function

import argparse
import os
import sqlite3
import subprocess
import sys
import time
import numpy as np
from subprocess import PIPE, Popen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../../')
from utils import (fs, gcard_helper, get_args,
                   scard_helper, user_validation, utils)

def add_new_user(username, domain_name, db, sql):
    """Add a user to the Users table."""

    strn = """
    INSERT INTO users(
        user, domain_name, join_date, total_submissions,
        total_events, priority
    )
    VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}");
    """.format(username, domain_name, utils.gettime(), 0, 0, 1)

    sql.execute(strn)
    db.commit()


def add_timestamp_to_submissions(timestamp, db, sql):
    """ Add a new entry to the UserSubmission table,
    this will auto-increment and assign a UserSubmissionID. """

    strn = """
    INSERT INTO submissions(client_time)
        VALUES ("{0}");""".format(timestamp)

    sql.execute(strn)
    db.commit()

    # The last row ID is the assigned UserSubmissionID
    # for this submission. Does the return value need
    # to be the lastrowid before commiting changes?
    return sql.lastrowid


def add_scard_to_submissions(scard, user_submission_id, db, sql):
    """Inject the scard raw into the table UserSubmissions """
    strn = """
    UPDATE submissions SET {0} = '{1}'
    WHERE user_submission_id = "{2}";
    """.format('scard', scard, user_submission_id)
    sql.execute(strn)
    db.commit()

def add_entry_to_submissions(usub_id, farm_name, db, sql):
    """ Create an entry in the FarmSubmissions table for this
    user submission.

    Inputs:
    -------
    usub_id - UserSubmissionID for this submission (int)
    gcard_id - GcardID for this submission (int)
    farm_name - Name of farm destination (str)
    sql - The database cursor object for writing.
    db - The database for committing changes.

    """

    strn = """
    UPDATE submissions SET run_status = 'Not Submitted'
    WHERE user_submission_id = '{0}';
    """.format(usub_id)
    sql.execute(strn)
    db.commit()


def update_user_information(username, user_id, user_submission_id, db, sql):
    """ Update the User and UserID for UserSubmissions.UserSubmissionID
    specified in arguments.

    Inputs:
    -------
    username - To set User (str)
    user_id - To set UserID (int), this comes from Users.UserID
    user_submission_id - Key for setting these in UserSubmissions table (int)
    db - Database connection for committing changes
    sql - Database cursor for execution of statements

    """

    update_template = """
    UPDATE submissions SET {0} = '{1}'
        WHERE user_submission_id = {2};
    """
    sql.execute(update_template.format('user_id', user_id, user_submission_id))
    db.commit()

    sql.execute(update_template.format('user', username, user_submission_id))
    db.commit()
