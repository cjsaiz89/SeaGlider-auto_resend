# SeaGlider-auto_resend
**Description**

Python and Bash scripts to auto resend missing files after a bad transmission 

Creates and deletes automatically the *pdoscmds.bat* file with the *resend_dive* command for each seaglider, after analyzing the *baselog.log* files. A copy of each log is made in the same directory where the scripts are located to avoid conflict while the base station is writing the log.

**Function of each script**

- **auto_pdos.sh** creates a */baselog_copies* directory, and copies/updates the baselog for each glider, named as *sgxxx.log*. Then, it executes the *auto_resend4.py*.

- **auto_resend4.py** parses the baselog copies, checks for missing files warnings, creates the necessary command sentence (i.e. *resend_dive d/ 120*), decides if the file needs to be created by checking the */sgxxx* directory looking for another active *pdoscmds.bat*, and the corresponding 'missing files' (it searches the *pxxxnnn.cap .log or .dat*), and if the claimed missing files are not in the directory, it will create the *pdoscmds.bat*, with the commands corresponding to only the missing files. At the end, it decides whether to delete and existing *pdoscmds.bat* or not, by checking it's content, looking for the files in the directory that are being requested to be resent by the *resend_dive /extension diveN*, and making sure to only delete the *pdoscmds.bat* only if it contains a *resend_dive* (don't use mixed commands if it's created manually).
After each time the script is run, it appends the outcome of the process to an *auto_resend.log* on each glider's directory. The information shown is date, time, current dive, creation or deletion of a *pdoscmds.bat* and its content.

**Execution**
1. Check that you have python and bash installed on the server with *python --version* and *bash --version*. 
2. The first time you run it, the bash script needs to be set as an executable file with *chmod +x auto_pdos.sh* typed in the terminal where the scipt is located.
3. Edit the list of seagliders in the *auto_pdos.sh* file.
4. Execute manually with *./auto_pdos.sh*
5. Execute automatically with *crontab*. Create a schedule (only one user should create it) by opening a *crontab* file. Type in the terminal *EDITOR=nano crontab -e*, to create and edit a with *nano*. Use *0 * * * * ./auto_pdos.sh* to execute at the top of each hour. Save and check with *crontab -l* that the changes were correctly made. Visit this webpage for reference [CRONTAB](https://crontab.guru/).

**How the *auto_resend4.py* reads the missing files from the *baselog.log*?**

The structure it looks for is:
> key-1
> 
> missing file 1
> 
> missing file 2
> 
> ...
> 
> missing file n
> 
> key-2

Being key-1 *The following files were not processed completely*, key-2 *Glider logout* and missing files are in lines starting with */home/*.

**Example**

baselog.log - last keys found:


       The following files were not processed completely:
          /home/sg663/sg0075dz.r
              Fragment /home/sg663/sg0075dz.x01 file size (4095) not equal to expected size (4096) - consider resend_dive /d 75 01

          /home/sg663/sg0078dz.r
              Fragment /home/sg663/sg0078dz.x01 file size (4095) not equal to expected size (4096) - consider resend_dive /d 78 01

      Glider logout seen - transmissions from glider complete

- Keep the names *sg0075dz.r* and *sg0078dz*
- Convert to *p6630075.dat* and *p6630078.dat*
- Search each file in */home/sg663* directory 
- Create a command and append to a list for each missing file in the directory. (*resend_dive /d 75* and *resend_dive /d 78*)
- Check that the requested dives to resend are not older than 5 dives from the current dive (i.e. current dive = 200, and baselog.lg claims missing p6630185 -> do not create, it's an old request. It was probably deleted to clean the dir and backed up). The current dive *NNN* is found from the greatest *cmdfile.NNN* found in the base station.
- Check if there's an active *pdoscmds.bat*. If there's one, check the content and only overwrite if a *resend_dive* is found.

- If all or any of the above conditions was not satisfied, don't create/update the *pdoscmds.bat*.

- If there is an active *pdoscmds.bat*, its content has a *resend_dive*, and the files requested to be resent are already in the seaglider directory, then delete the *pdoscmds.bat*

