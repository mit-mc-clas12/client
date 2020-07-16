"""
Tests for update_tables.  A database is built in memory that
mimics the structure of our full database.
"""

# Standard Lib
import os
import unittest
import sqlite3
import sys

# Local
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../src/')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../')
import update_tables
from utils import fs, utils


def add_field(db, sql, tablename, field_name, field_type):
    strn = "ALTER TABLE {0} ADD COLUMN {1} {2}".format(
        tablename, field_name, field_type)
    sql.execute(strn)
    db.commit()


def create_table(db, sql, tablename, PKname, FKargs):
    strn = ("CREATE TABLE IF NOT EXISTS {0}({1} INTEGER"
            " PRIMARY KEY AUTOINCREMENT {2})").format(
                tablename, PKname, FKargs)
    sql.execute(strn)
    db.commit()


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        """ Setup a testing database for this problem. """
        self.db = sqlite3.Connection(':memory:')
        self.sql = self.db.cursor()

        for table, primary_key, foreign_keys in zip(
                fs.tables, fs.PKs, fs.foreign_key_relations):
            create_table(self.db, self.sql, table, primary_key, foreign_keys)

        for i, table in enumerate(fs.tables):
            for field, field_type in fs.table_fields[i]:
                add_field(self.db, self.sql, table, field, field_type)

        self.scard = """
        project:  CLAS12
        farm_name: OSG
        gcards: /jlab/clas12Tags/gcards/clas12-default.gcard
        generator: https://userweb.jlab.org/~ungaro/lund/
        generatorOUT: yes
        gemcEvioOUT: yes
        gemcHipoOUT: yes
        reconstructionOUT: yes
        dstOUT: yes
        """

    def tearDown(self):
        """ Close testing database. """
        self.db.close()

    def test_add_user(self):
        """ Test the addition of a user into the database. """
        user = 'TestUser'
        update_tables.add_new_user(user, 'TestDomain', self.db, self.sql)
        self.sql.execute('SELECT user FROM users')
        results = self.sql.fetchall()[0][0]
        self.assertEquals(results, user)

    def test_add_entry_to_submissions(self):
        """ Test the addition of an entry into UserSubmissions table. """
        for i in range(10):
            uid = update_tables.add_timestamp_to_submissions(
                utils.gettime(), self.db, self.sql)
            self.assertEquals(uid, i+1)

    def test_add_scard_to_submissions(self):
        """ Try adding an scard to the user information
        and retrieving it again. """

        # Create a test submission to get user submission id
        uid = update_tables.add_entry_to_submissions(
            utils.gettime(), self.db, self.sql)
        update_tables.add_scard_to_submissions(
            self.scard, uid, self.db, self.sql)

        self.sql.execute(
            ("SELECT scard FROM submissions WHERE "
             " user_submission_id = {}").format(uid))
        result = self.sql.fetchall()[0][0]
        self.assertEquals(self.scard, result)


if __name__ == "__main__":
    unittest.main()
