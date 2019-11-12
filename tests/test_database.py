""" 
Tests for update_tables.  A database is built in memory that 
mimics the structure of our full database. 
"""

# Standard Lib 
import os 
import unittest 
import sys 

# Third Party (?)
import sqlite3

# Local 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../src/')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../')
from utils import fs, utils 
import update_tables 

def add_field(db, sql, tablename, field_name, field_type):
  strn = "ALTER TABLE {0} ADD COLUMN {1} {2}".format(tablename, field_name, field_type)
  sql.execute(strn)
  db.commit() 
  
def create_table(db, sql, tablename, PKname, FKargs):
  strn = "CREATE TABLE IF NOT EXISTS {0}({1} INTEGER PRIMARY KEY AUTOINCREMENT {2})".format(tablename, PKname, FKargs)
  sql.execute(strn)
  db.commit() 

class DatabaseTest(unittest.TestCase):

  def setUp(self):
    """ Setup a testing database for this problem. """
    self.db = sqlite3.Connection(':memory:')
    self.sql = self.db.cursor() 
    
    for table, primary_key, foreign_keys in zip(fs.tables, fs.PKs, fs.foreign_key_relations):
      create_table(self.db, self.sql, table, primary_key, foreign_keys)
      
    for i, table in enumerate(fs.tables):
      for field, field_type in fs.table_fields[i]:
        add_field(self.db, self.sql, table, field, field_type)

    self.scard = """
    project:  CLAS12                                      # project name
    farm_name: OSG                                        # farm pool
    gcards: /jlab/clas12Tags/gcards/clas12-default.gcard  # gcard within the container
    generator: https://userweb.jlab.org/~ungaro/lund/    # online location containing LUND files
    generatorOUT: yes                                     # keep the generated file
    gemcEvioOUT: yes                                      # keep the gemc evio output
    gemcHipoOUT: yes                                      # keep the gemc decoded (hipo) output
    reconstructionOUT: yes                                # keep the output from reconstruction
    dstOUT: yes                                           # keep the DST
    """

  def tearDown(self):
    """ Close testing database. """
    self.db.close() 

  def test_add_user(self):
    """ Test the addition of a user into the database. """
    user = 'TestUser'
    update_tables.add_new_user(user, 'TestDomain', self.db, self.sql)    
    self.sql.execute('SELECT User FROM Users')
    results = self.sql.fetchall()[0][0]
    self.assertEquals(results, user)
  
  def test_add_entry_to_user_submissions(self):
    """ Test the addition of an entry into UserSubmissions table. """
    for i in range(10):
      uid = update_tables.add_entry_to_user_submissions(utils.gettime(), self.db, self.sql)
      self.assertEquals(uid, i+1)

  def test_add_scard_to_user_submissions(self):
    """ Try adding an scard to the user information and retrieving it again. """
 
    # Create a test submission to get user submission id 
    uid = update_tables.add_entry_to_user_submissions(utils.gettime(), self.db, self.sql)
    update_tables.add_scard_to_user_submissions(self.scard, uid, self.db, self.sql)
 
    self.sql.execute('SELECT scard FROM UserSubmissions WHERE UserSubmissionID = {}'.format(uid))
    result = self.sql.fetchall()[0][0]
    self.assertEquals(self.scard, result)

  def test_add_scard_to_scards_table(self):
    """ Trying to add the scard to the scards table, this might be removed. """

    # Create a dictionary structure for the scard 
    data = {}
    for line in self.scard.split('\n'):
      if line:
        tokens = line.split()

        if len(tokens) > 1:
          field = tokens[0].split(':')[0]
          value = tokens[1]
          data[field] = value

    # Create a test submission to get user submission id 
    uid = update_tables.add_entry_to_user_submissions(utils.gettime(), self.db, self.sql)
    update_tables.add_scard_to_scards_table(data, uid, utils.gettime(), self.db, self.sql)
    
    # Add the field to the scards table, then get it back and make sure it works
    for field, value in data.items():
      self.sql.execute('SELECT {} FROM Scards WHERE UserSubmissionID = {}'.format(field, uid))
      result = self.sql.fetchall()[0][0]
      self.assertEquals(result, value)

    def test_add_gcard_to_gcards_table(self):
      """ Add/retrieve a gcard to test that it is the same and our 
      function successfully inserts. """
      gcard_text = 'asdijzlkasjdfjxc'
      uid = update_tables.add_entry_to_user_submissions(utils.gettime(), self.db, self.sql)
      update_tables.add_gcard_to_gcards_table(gcard_text, uid, self.db, self.sql)
      
      self.sql.execute('SELECT gcard_text FROM Gcards WHERE UserSubmissionID = {}'.format(uid))
      result = self.sql.fetchall()[0][0]
      self.assertEquals(gcard_text, result)

if __name__ == "__main__":
  unittest.main()
    
