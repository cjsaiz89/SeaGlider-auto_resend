#****************************************************************************
#******* AUTO RESEND v4 *****************************************************
# auto_pdos.sh and auto_resend4.py must be in the same directory

############################################################################################
# SCRIPT START - DON'T CHANGE ANYTHING 

# ALT+MC to show line number
# ALT+MI auto justify

###########################################
# Import libraries
import os
import datetime

###########################################
# Import list of seagliders from bash
ids_bash = os.environ['ids']
global glider_list
glider_list = ids_bash.split()

###########################################
# Open baselog file

def process_baselog(glider_id):

	src_path = 'baselog_copies/'+glider_id+'.log'

	try:
		f = open(src_path)
		print('File '+src_path+ ' opened')
	except:
		print('File '+src_path+ ' not found')

	# Read each line
	if(f):
		n = 0
		while True:
		#for line in f:
			line = f.readline()
			# Detect end of file and stop loop
			if not line:
				break
			
			if('following files were not processed completely' in line):
				# Now keep lines starting in '/home/ until 'Glider logout seen'
				#print('---------------------------------------------')
				#print('following...found -> clearing same_dive list')				
				same_dive = [] # list of lines belonging to same dive
				while True: 
					sub_line = f.readline() # read next line from file
				#	print('subline: ' + sub_line)
					if sub_line.startswith('    /home/'): # if starts with /home is the missing file
						sub_line = sub_line.split('/')[-1] # keep last part belonging to the file as /home/sg663/sg0276dz.r
				#		print('subline file: ' + sub_line)
						same_dive.append(sub_line) # append to list of missing files in current dive
					
					if 'Glider logout' in sub_line:
				#		print('Glider logout BREAK')
						break # break loop because there are no more missing files in current dive
				#print('------------------')
				#print('Same_dive list:')
				#print(same_dive)
				#print('------------------')
				# at this point there's a list with files missing in current dive in the form of sg0276dz.r
				# create a command for each file
				#print('Creating commands...')
				command_string = ''
				inc_diveN = ''
				k = 0
				for element in same_dive:
					inc_file = element.split('.')[0] # split incomplete file name and grab first part as sg0276dz
					inc_file = inc_file.replace('sg','') # delete sg and remains 0276dz
					file_type = inc_file[-2] # get 2nd to last char -> c, l or d
					if file_type == 'k':
						file_type = 'c'
					inc_diveN = int(inc_file[0:4]) # dive number is a fixed 4 digit number. Convert to integer
					
				#	print('------------------')
					cmd = 'resend_dive /' + file_type + ' ' + str(inc_diveN)
				#	print(str(k) + ' -> ' + cmd)
					# stack commands into one string
					command_string = command_string + cmd + '\n'
					k = k + 1
				# Increase number of incomplete messages
				n = n + 1
				# print commands within last loop
				#print('pdoscmd text:\n' + command_string)
				#print('---------------------------------------------')

			
	f.close() 
	print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%")
	print('Last dive claiming an incomplete processed file: ' + str(inc_diveN) + '\nCommands:\n' + command_string)
	print("%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
	print(str(n)+ ' lines with incomplete files')
	info_pair = [0,0]
	info_pair[0] = inc_diveN # last incomplete dive that needs to be resent as integer
	info_pair[1] = command_string # command text for .bat file
	return info_pair

###########################################
# Get last dive from directory

def get_last_cmdfile(glider_id):

	src_path = '/home/'+glider_id
	file_list = os.listdir(src_path)
	
	dive_list = []
	for x in file_list:
		if x.startswith('cmdfile'):
			try:
				dive_num = x.split('.')[1] # keep number after dot
				dive_num = int(dive_num)
				dive_list.append(dive_num) # keep only cmdfile copies
			except: # for the case of the original cmdfile
				pass	
	#print('\nDive list:\n')
	#print(dive_list)
	dive_list.sort() # sort list of dives in the same list
	#print('Dive list sorted:')
	#print(dive_list)			
	last_dive = dive_list[-1]
	print('Last dive found in ' + src_path + ' -> ' + str(last_dive))

	return last_dive # return as integer


###########################################
# Get last pdoscmd.bat

def search_bat(glider_id):
	
	src_path = '/home/'+glider_id
	file_list = os.listdir(src_path)
	active = False
	pdos_list = []
	for x in file_list:
		if x.startswith('pdoscmds'):
			if x.endswith('.bat'):
				active = True
	return active


###########################################
# Check text in .bat file

def check_bat_content(glider_id):
	src_path = '/home/' + glider_id + '/pdoscmds.bat'
	f = open(src_path)
	bat_content = []
	if f:
		print('pdoscmds.bat opened...')
		for line in f:
			bat_content.append(line)	
	f.close()
	print('---------------------------------------------')
	print('pdoscmds.bat content:')
	print(bat_content)
	print('---------------------------------------------')
	bat_string = ''
	for line in bat_content:
		bat_string = bat_string + line
	return bat_string # return list with content


###########################################
# Convert number to 4 digit format

def num4digit(num):

	ns = ''
	if num < 1:
		ns = '0000'
	elif num < 10:
		ns = '000' + str(num)
	elif num < 100:
		ns = '00' + str(num)
	elif num < 1000:
		ns = '0' + str(num)
	elif num < 10000:
		ns = str(num)

	return ns	

def num2digit(num):
	n = ''
	if num < 1:
		n = '00'
	elif num < 10:
		n = '0' + str(num)
	else:
		n = str(num)
	
	return n
		

###########################################
# Convert command lines to file names missing

def cmd2file( glider_id, txt):
	print('Converting command to file name...')
	cmd2list = txt.split('\n') # if more than one line split each and store as list
	print('cmd2list: ')
	print(cmd2list)
	file_list = []
	for line in cmd2list:
		if len(line) > 2:
			linels = line.split() # split by space [resend_dive, /x, yyy]
			print('line: ')
			print(linels)
			diveN = num4digit( int(linels[2]) ) # return 4 digit number
			ftype = linels[1].replace('/','') # delete slash
			# get file extension
			ext = ''
			if ftype == 'd':
				ext = '.dat'
			if ftype == 'c':
				ext = '.cap'
			if ftype == 'l':
				ext = '.log'
			file = 'p' + glider_id.replace('sg','') + diveN + ext	 
			file_list.append(file)

	#print(file_list)
	return file_list


###########################################
# Convert cmd text to list

def cmd2list(txt):

	print('Converting command to file name...')
        cmd2list = txt.split('\n') # if more than one line split each and store as list
        cmdls = []
	for cmd in cmd2list:
		if len(cmd) > 2:
			cmdls.append(cmd) # append command line only and filter out \n char
	
	return cmdls # list of commands  


###########################################
# Search for files that according to resend_dive command should be resent

def search_files( glider_id, files2search):

	src_path = '/home/'+glider_id
        files_in_dir = os.listdir(src_path) # list containing all files in the directory including .dat .log .cap
	foundls = []
	for file in files2search: # for each file to search
		if file in files_in_dir: # if it's in the directory 1, else 0
			foundls.append(1)
		else:
			foundls.append(0)

	return foundls # list of files found [1] or not found [0]
			
###########################################
# List of dives to be resent

def get_last_dive(flist):
	
	lst = [] # list of dives to resend
	for f in flist:
		dive = f.split('.')[0]
		dive = int(dive[4:])
		lst.append(dive)
	lst.sort()
	print('Dives to resend:')
	print(lst)
	return lst[-1] # return last dive to return as integer


###########################################
# check whether to create a new .bat file w/commands or not

def get_final_cmd( glider_id, info_pair, last_cmd_dive):
	
	# --- Condition 1 --- search active pdoscmds.bat
        cond1 = False # first condition to create .bat
        if search_bat(glider_id): # check active pdoscmd.bat True/False
                print('BAT file active') # if active, check the content
                bat_string = check_bat_content(glider_id) #  .bat content
                # if content contains 'resend_dive' overwrite, otherwise (target or other command) don't
                if 'resend_dive' in bat_string:
                        print('bat file can be overwritten')
                        cond1 = True # if there's a resend_dive, is old or is the same .bat we want to create. No problem here
               	else:
                        print('do not overwrite bat file')
			cond1 = False # remain false, we don't want to change it if it's another command
	else:
        	print('No active BAT file')
		save_log(glider_id,'No active BAT file')
           	# if there's no .bat file, no danger to write a new one
           	cond1 = True
	
	# --- Condition 2 --- search existing files in directory
        # check if required files to be resent are already there. Search .dat .log and .cap
        # format ex. p6630298.log p6630298.dat p6630298.cap
	cmdls = cmd2list(info_pair[1]) # list of commands in same order as files2search
	files2search = cmd2file(glider_id,info_pair[1]) # list of files to search
	print('Files to search:')
	print(files2search)
	files_found = search_files(glider_id,files2search) # list of files found in order: 1 found, 0 not found ex. [1,0,0] for 3 files
	print('Found files binary [1 found, 0 not found]:') 
	print(files_found)	
	print('Last dive to resend:')
	last2resend = get_last_dive(files2search) # greatest dive number to be resent
	print(last2resend)
	# For each command check which one need to be sent according to files found
	n = 0
	filtered_cmds = ''
	for cmd in cmdls:
		if  files_found[n] == 0: # if corredponding file was not found, request resend, else don't
			filtered_cmds = filtered_cmds + cmd + '\n'
		else:
			print('File corresponding to ' + cmd + ' already exists' )
		n = n + 1
	
	# --- Condition 3 --- dive to be resent must be not more than 10 dives older than last dive
	cond3 = False
	if ( (last_cmd_dive - last2resend) < 5 ):	
		cond3 = True
		print('File to resend is recent')
		
	else:
		print('File to resend is greater than 5 dives old')

	# -- FINAL DECISION
	final_cmd = ''
	if cond1 and cond3 and len(filtered_cmds)>2:
		final_cmd = filtered_cmds
	else:
		final_cmd = 'NO'	
	
	return final_cmd # return the command text to create .bat file or NO to not create the file 

###########################################
# Create pdoscmds.bat file in glider directory after passing the filters

def create_pdos(glider_id,cmd):
	
	dst_path = '/home/' + glider_id + '/pdoscmds.bat'
	#dst_path = 'pdoscmds.bat' # test locally 
	fout = open(dst_path,'w')
	fout.write(cmd)
	fout.close()
	print('***********************************')
	save_log(glider_id,'**************************************')
	print('File created:' + dst_path)
	save_log(glider_id,'-> File created: ' + dst_path)
	print('Content:')
	save_log(glider_id,'Content:')
	print(cmd)
	save_log(glider_id,cmd)
	print('***********************************')
	save_log(glider_id,'**************************************')
	
###########################################
# Decide to delete the .bat only if all files already exist, and the content has a resend_dive
def decide_delete(glider_id):

        delete = False
        # check .bat active
        if search_bat(glider_id):
        	print('Active pdoscmds.bat found')
		# read content
                bat_string = check_bat_content(glider_id)
                if 'resend_dive' in bat_string:
			print('File contains resend_dive')
			save_log(glider_id,'File content:')
			save_log(glider_id,bat_string)
                        cmdls = cmd2list(bat_string) # .bat string content to list
                        files2search = cmd2file(glider_id,bat_string) # list of files to search
                        files_found = search_files(glider_id,files2search) # list of files found -> 1 found, 0 not found
                        # if all files found, delete .bat
                        print('Files to search:')
                        print(files2search)
                        print('Files found:')
                        print(files_found)
			# check if ALL files were found
			all_found = True
			for bit in files_found:
				all_found = (all_found and bit) # do a A & B for every file. If one is 0, result is 0. If all 1, result is 1					
                        # if all were found, then delete 
			if all_found == True:
				delete = True
				dst_path = '/home/' + glider_id + '/pdoscmds.bat' # remove .bat
				os.remove(dst_path)
				print(dst_path + ' deleted')
	else:
		print('No active pdoscmds.bat found')
	
        return delete


###########################################
# save info to log file
def save_log(glider_id,text):

	dst_path = '/home/' + glider_id + '/auto_resend.log'
	flog = open(dst_path, 'a')
	flog.write(text + '\n')
	flog.close()

###########################################
# get current date and time as string
def date_time():

	now = datetime.datetime.now()
		
	return num2digit(now.month)+'-'+num2digit(now.day)+'-'+str(now.year)+'  '+num2digit(now.hour)+':'+num2digit(now.minute)+':'+num2digit(now.second)


############################################################################################
# MAIN

def main():
	
	txt = ''
	count = 0
	for a in glider_list:
		txt = txt + a + ' - '
		count = count + 1
	print('STARTING ANALYSYS ON ' + txt)
	
	for glider_id in glider_list: 
		print('--------------------------------------------------------------------------------------------')
		print('Analyzing ' + glider_id)
		save_log(glider_id,'--------------------------------------------------------------------------------------------')
		save_log(glider_id,date_time() + ' - ' + glider_id)
		print('////////////////////////////')
		print('\nOpening baselog file...\n')
		info_pair = process_baselog(glider_id) # returns last dive incomplete [0] and text command for .bat file [1]
		inc_last_dive = info_pair[0] # last dive that needs to be resent as integer
		command = info_pair[1] # string of commands to create .bat file
		print('End of baselog process')
		print('////////////////////////////')
	 	print('\nSearching cmdfiles in dir...\n')
		cmdfile_last_dive = get_last_cmdfile(glider_id) # returns last dive found in glider directory cmdfile.xxx as integer. Use as real last dive 
		save_log(glider_id,'Last dive in directory: ' + str(cmdfile_last_dive))
		print('////////////////////////////')
		#print('\nFROM MAIN:\n')
		#print('Last incomplete dive: ' + str(inc_last_dive) + '\nLast cmdfile.dive: ' + str(cmdfile_last_dive) + ' \nCommand:\n' + command )
		#print('////////////////////////////')
	
		print('Deciding to create pdoscmds.bat...')
		final_cmd = get_final_cmd(glider_id,info_pair,cmdfile_last_dive) # returns the final command text to create .bat file. If 'NO', then don't create file.	
		print('final_cmd result: ')
		print(final_cmd)
		if final_cmd != 'NO' and final_cmd != '':
			print('Creating pdoscomds.bat...')
			create_pdos(glider_id,final_cmd)
		else:
			print('Decided not to create pdoscmds with the following commands:')
			print(command)
			save_log(glider_id,'pdoscmds.bat not created')
		
		print('Deciding to delete pdoscmds.bat...')
		if decide_delete(glider_id):
			print('pdoscmds.bat deleted')
			save_log(glider_id,'-> File/s found in directory: pdoscmds.bat deleted')
		else:
			print('pdoscmds.bat not deleted')
			save_log(glider_id,'pdoscmds.bat not deleted')
		print('////////////////////////////')
		
		
		print(glider_id + ' - done')
 		print('--------------------------------------------------------------------------------------------')
		save_log(glider_id,glider_id + ' - done')
	
	print('ALL ' + str(count) + ' GLIDERS WERE ANALYZED')
	
	print('PROGRAM FINISHED')
	
############################################################################################
if __name__ == "__main__":
	main()
