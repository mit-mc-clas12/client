"""Module for reading the raw SCard, returns an SCard class object. """


from __future__ import print_function
import os
import sys

# Configure the current script to find utilities. 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../')
from utils import fs, scard_helper, utils

def scard_handler(args, UserSubmissionID, timestamp):
  """Handle the raw scard and return the fields as an scard object. 

  This function currently has a lot of responsibility including 
  injection into the database.  Suggest splitting it into smaller
  functions for testability. 

  1) Open the raw scard.
  2) Convert it to an instance of scard_class, this runs 
     the raw file through a parser, catching some errors
     and can potentially exit to system.
  3) Write the contents of the scard into the UserSubmissions table.
  4) Fix some data from the scard (this should be in the parser function).
  5) Inject the scard into the SCards table (may not be needed, 
     waiting to see).
  6) Return the scard_class instance to the main code.

  """
  scard_file = args.scard

  # Load the raw scard file into memory and convert it 
  # to an instance of scard_class. 
  with open(scard_file, 'r') as file: 
    scard = file.read()
  
  scard_fields = scard_helper.scard_class(scard)
  

  # Inject the scard into the database. 
  strn = """
  UPDATE UserSubmissions SET {0} = '{1}' 
      WHERE UserSubmissionID = "{2}";""".format(
        'scard', scard, UserSubmissionID
  )
  utils.db_write(strn)
  utils.printer( ("UserSubmission specifications written to database "
                  "with UserSubmissionID {0} from scard {1}").format(
                    UserSubmissionID, scard_file))
 
  """
  'group' is a protected word in SQL so we can't use the field title "group"
  For more information on protected words in SQL, see: 
  https://docs.intersystems.com/irislatest/csp/docbook/
  DocBook.UI.Page.cls?KEY=RSQL_reservedwords
  """
  scard_fields.data['group_name'] = scard_fields.data.pop('group') 
  
  # Set event generator executable and output to null if the 
  # generator doesn't exist in our container.  We are 
  # trying to keep the client agnostic to SCard type. 
  scard_fields.data['genExecutable'] = fs.genExecutable.get(
    scard_fields.data.get('generator'), 'Null'
  )
  scard_fields.data['genOutput'] = fs.genOutput.get(
    scard_fields.data.get('generator'), 'Null'
  )

  
  scard_helper.SCard_Entry(UserSubmissionID, timestamp, scard_fields.data)
  print(("\t Your scard has been read into the database "
         "with UserSubmissionID = {0} at {1} \n").format(
           UserSubmissionID, timestamp)
      )

  return scard_fields

def add_scard_to_user_submissions(scard):
  """Add the current scard into the UserSubmissions table. """
  
