#!/usr/bin/env bash

echo "-----------------------"
echo "Starting auto_pdos"

# ------- EDIT BY USER SECTION -----------------------------------------------------------------------
# Select Seagliders to copy baselog. Make sure the same gliders are in the auto_resend2.py script
declare -a sg_list=("sg663" "sg667" "sg668" "sg649" "sg669" "sg670")

# -----------------------------------------------------------------------------------------------------

# ------ WARNING - DO NOT CHANGE FROM HERE ---------------------------------------------------------------------
# Create directory to store baselog copies if it doesn't exist yet
new_dir=$(pwd)/baselog_copies
mkdir -p $new_dir

# Copy baselog from each sgxxx folder
for i in ${sg_list[@]}
do
	# copy only if different with -u update
	cp -u /home/$i/baselog.log $new_dir/$i.log
	echo "Baselog from /home/$i updated to $new_dir"
done

echo "Done updating baselogs"
echo "-----------------------"
echo ""
echo "Executing python script..."
echo ""

# export list to shell environment for use in python script
export ids="${sg_list[@]}"

# After copying baselog, execute python script
# NOTE: Comment the following command to stop auto_resend script
python auto_resend4.py





