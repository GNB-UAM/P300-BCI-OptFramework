#!/bin/bash

# Check if the arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <root_dir>";
    exit 1;
fi

root_dir="$1";
mapfile -d '' databases < <(find "$root_dir" -name "*.db" -print0)

# keys to delete
i=0
n=${#databases[@]}
keys=("CV_Evid" "CV_StimSeq" "CV_StimTgt")
for db in "${databases[@]}"; do
	for k in "${keys[@]}"; do
		sqlite3 -line "$db" "DELETE FROM trial_user_attributes WHERE key='$k'";
		sqlite3 -line "$db" "VACUUM";
	done;
	((i++));
	echo -e "====$db done! ($i/$n)====\n";
done;

