"""Module for reading the raw SCard, returns an SCard class object. """


from __future__ import print_function
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../')
from utils import fs, get_args, scard_helper, utils

def scard_handler(args, UserSubmissionID, timestamp):
  scard_file = args.scard

  # Write the text contained in scard.txt to a field in the 
  # UserSubmissions table
  with open(scard_file, 'r') as file: 
    scard = file.read()
  
    strn = """
    UPDATE UserSubmissions SET {0} = '{1}' 
    WHERE UserSubmissionID = "{2}";""".format(
      'scard', scard, UserSubmissionID
    )
  utils.db_write(strn)
  utils.printer( ("UserSubmission specifications written to database "
                  "with UserSubmissionID {0}").format(UserSubmissionID))

  # See if user exists already in database; if not, add them
  with open(scard_file, 'r') as file: 
    scard_text = file.read()
  scard_fields = scard_helper.scard_class(scard_text)

  # Write scard into scard table fields (This will not be needed in the future)
  print("\nReading in information from {0}".format(scard_file))
  utils.printer("Writing SCard to Database")

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

if __name__ == "__main__":
  args = get_args.get_args_client()
  scard_handler(args, UserSubmissionID, timestamp)
