"""Module for reading the raw SCard, returns an SCard class object. """


from __future__ import print_function
import fs, utils
import scard_helper_new as scard_helper
import os
import sys

# Configure the current script to find utilities.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../')


#def scard_handler(args, UserSubmissionID, timestamp):
#    """Handle the raw scard and return the fields as an scard object.
#
#    1) Open the raw scard.
#    2) Convert it to an instance of scard_class, this runs
#       the raw file through a parser, catching some errors
#       and can potentially exit to system.
#    3) Write the contents of the scard into the UserSubmissions table.
#    4) Inject the scard into the SCards table (may not be needed,
#       waiting to see).
#    5) Return the scard_class instance to the main code.
#
#    This function is under construction.
#    """
#    scard_file = args.scard
#
#    # Load the raw scard file into memory and convert it
#    # to an instance of scard_class.
#    with open(scard_file, 'r') as file:
#        scard = file.read()
#
#    scard_fields = scard_helper.scard_class(scard)
#
#    # Inject the scard into the UserSubmissions table.
#    strn = """
 # UPDATE UserSubmissions SET {0} = '{1}'
#      WHERE UserSubmissionID = "{2}";""".format(
#        'scard', scard, UserSubmissionID
#    )
#    utils.db_write(strn)
#    utils.printer(("UserSubmission specifications written to database "
#                   "with UserSubmissionID {0} from scard {1}").format(
#        UserSubmissionID, scard_file))
#
#    # Inject the scard into the SCards table.
#    scard_helper.SCard_Entry(UserSubmissionID, timestamp, scard_fields.data)
#    print(("\t Your scard has been read into the database "
#           "with UserSubmissionID = {0} at {1} \n").format(
#        UserSubmissionID, timestamp)
#    )
#
#    return scard_fields
#

def open_scard(scard_filename):
    """Temporary function name, to provide functionality of
    the function above. """
    with open(scard_filename, 'r') as scard_file:
        scard = scard_file.read()

    # Get a class instance, this parses the scard.
    # Append the raw text to the object, it is not
    # really much memory so I think this is fine.
    # It becomes useful instead of re-opening the
    # file multiple times to have the raw text.
    scard_fields = scard_helper.scard_class(scard)

    scard_fields.raw_text = scard


    return scard_fields


def get_scard_type(scard_filename):
    """ Returns the type of scard by inspecting the name
    of the scard file.  This can be replaced by a function
    that inspects the contents of the scard and infers the
    type.  Such a function already exists in server/type_manager.
    That can be migrated to utilities if needed.  For now
    this simple approach is okay, because the web_interface
    always names the scard with the type in the name.

    Input:
    ------
    scard_filename - The name of the scard file (str).

    Returns:
    --------
    scard_type - The type of the scard, can be None if
                 none of the allowed types are found in the name.
    """
    scard_type = None
    for possible_type in fs.valid_scard_types:

        name = 'type{0}'.format(possible_type)
        if name in scard_filename:
            scard_type = possible_type

    return scard_type
