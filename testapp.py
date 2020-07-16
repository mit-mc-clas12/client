import subprocess
import os
#this is a comment


class command_class:
	def __init__(self,command_name,command_string,expected_output):
		self.name = command_name
		self.command = command_string
		self.expect_out = expected_output





def test_function(command):
	process = subprocess.Popen(command.command,
		stdout=subprocess.PIPE, 
		stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()


	if command.expect_out != '0':
		if stdout == command.expect_out:
			return(stdout,stderr)
		else:
			err_mess = str(stderr) + "unexpected sdtout of: " + str(stdout)
			return(stdout, err_mess)
	else:
		return(stdout,stderr)



test_folder= os.path.dirname(os.path.abspath(__file__))+'/clas12-test'
print(test_folder+" is present, not re-cloning")
if os.path.isdir(test_folder):
	print('removing previous database file')
	subprocess.call(['rm','-rf',test_folder])
if os.path.isdir(test_folder):
	print('removing previous database file')
	subprocess.call(['rm','-rf',test_folder])



subprocess.call(['mkdir','-p','clas12-test'])


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)+'/clas12-test'
os.chdir(dname)


#subprocess.call(['cd','clas12-test'])



folders = ['utils','server','client']
for folder in folders:
	folder_name= os.path.dirname(os.path.abspath(__file__))+'/'+folder
	if not os.path.isdir(folder_name):
		print('{0} not found, cloning from github'.format(folder))
		substring = 'https://github.com/robertej19/{0}.git'.format(folder)
		subprocess.call(['git','clone',substring])



filename = os.path.dirname(os.path.abspath(__file__))+'/utils/CLAS12OCR.db'
if os.path.isfile(filename):
	print('removing previous database file')
	subprocess.call(['rm',filename])


create_sqlite_db = command_class('Create SQLite DB',
								['python2', 'utils/create_database.py','--lite=utils/CLAS12OCR.db'],
								'0')

submit_scard_1 = command_class('Submit scard 1 on client',
								['python2', 'client/src/SubMit.py','--lite=utils/CLAS12OCR.db','-u=robertej','client/scards/scard_type1.txt'],
								'0')

#submit_scard_2 = command_class('Create scard 2 on client',
#								['python2', 'client/src/SubMit.py','--lite=utils/CLAS12OCR.db','-u=robertej','client/scard_type2.txt'],
#								'0')

verify_submission_success = command_class('Verify scard submission success',
								['sqlite3','utils/CLAS12OCR.db','SELECT user FROM submissions WHERE user_submission_id=1'],
								'robertej\n')



submit_server_jobs = command_class('Submit jobs from server',
								['python2', 'server/src/Submit_UserSubmission.py', '-b','1', '--lite=utils/CLAS12OCR.db', '-w', '-s', '-t'],
								'0')


command_sequence = [create_sqlite_db, submit_scard_1, verify_submission_success,submit_server_jobs]


def run_through_tests(command_sequence):
	err_sum = 0 
	for command in command_sequence:
		out, err = test_function(command)
		print('Testing command: {0}'.format(command.name))
		if not err:
			print('... success')
			#print(out)
		else:
			print(out)
			print('... fail, error message:')
			print(err)
			err_sum += 1
			
	return err_sum



status = run_through_tests(command_sequence)
if status > 0:
	exit(1)
else:
	exit(0)



"""
#which condor_submit if val = 0, do not submit, print not found message
"""
