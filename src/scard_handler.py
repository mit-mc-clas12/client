"""Module for reading the raw SCard, returns an SCard class object. """


from __future__ import print_function
import os
import sys

# Configure the current script to find utilities. 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../')
from utils import fs, scard_helper, utils

def scard_handler(args, UserSubmissionID, timestamp):
  """Handle the raw scard and return the fields as an scard object. 

  1) Open the raw scard.
  2) Convert it to an instance of scard_class, this runs 
     the raw file through a parser, catching some errors
     and can potentially exit to system.
  3) Write the contents of the scard into the UserSubmissions table.
  4) Inject the scard into the SCards table (may not be needed,  
     waiting to see).
  5) Return the scard_class instance to the main code.

  This function is under construction. 
  """
  scard_file = args.scard

  # Load the raw scard file into memory and convert it 
  # to an instance of scard_class. 
  with open(scard_file, 'r') as file: 
    scard = file.read()
  
  scard_fields = scard_helper.scard_class(scard)
  
  # Inject the scard into the UserSubmissions table. 
  strn = """
  UPDATE UserSubmissions SET {0} = '{1}' 
      WHERE UserSubmissionID = "{2}";""".format(
        'scard', scard, UserSubmissionID
  )
  utils.db_write(strn)
  utils.printer( ("UserSubmission specifications written to database "
                  "with UserSubmissionID {0} from scard {1}").format(
                    UserSubmissionID, scard_file))

  # Inject the scard into the SCards table.
  scard_helper.SCard_Entry(UserSubmissionID, timestamp, scard_fields.data)
  print(("\t Your scard has been read into the database "
         "with UserSubmissionID = {0} at {1} \n").format(
           UserSubmissionID, timestamp)
      )

  return scard_fields

def inject_scard_into_user_submissions(scard, user_submission_id, sql):
  """Inject the scard raw into the table UserSubmissions """
  insertion = """
  UPDATE UserSubmissions SET {0} = '{1}'
      WHERE UserSubmissionID = "{2}";
  """.format('scard', scard, user_submission_id)
  sql.execute(insertion)

def open_and_inject_scard(scard_filename, user_submission_id, timestamp, sql):
  """Temporary function name, to provide functionality of 
  the function above. """
  with open(scard_filename, 'r') as scard_file:
    scard = scard_file.read() 

  # Get a class instance, this parses the scard. 
  scard_fields = scard_helper.scard_class(scard)
  
  # Inject card into database 
  inject_scard_into_user_submissions(scard, user_submission_id, sql)

  # The scard can also be injected into the scards table 
  # here but I don't think we need to do that so for now 
  # I am not writing that functionality. 
  return scard_fields 
