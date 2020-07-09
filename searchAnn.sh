#!/bin/sh

# Title: Announcement Analysis
# Name: Justin Buhagiar
# Last edited: 9/7/20

date="$1"
pdfToTxt="true"

pdfs="announcement_files/pdfs"
texts="announcement_files/texts"
reports="announcement_files/reports"

# If no argument todays date is used
if [ "$#" -lt 1 ] 
then
	date="$(date +'%d-%m-%Y')"
fi

# Checks arguments are correct and folders exist
if [ ! -d "$pdfs/$date" ]
then
	if [ -d "$texts/$date" ]
	then 
		pdfToTxt="false"
	else
	echo "Directory '$pdfs/$date' DOES NOT exist."
	echo "Usage: ./seachAnn.sh <dd-mm-yyyy>"
	exit 1
	fi
fi

# Converts all pdfs to txt, deletes pdfs and put txt into seperate folder
# Doesn't overite txt file if it already exists
if "$pdfToTxt" = "true"
then
	echo "Converting pdf files to txt. This may take some time..."

	if [ ! -d "$texts/$date" ]
	then
		mkdir "$texts/$date"
	fi

	for file in "$pdfs/$date/"*
	do 	
		code=`echo "$file" | cut -d'/' -f4 | cut -c 1-3`
		fileName=`echo "$file" | cut -d'/' -f4 | cut -d'.' -f1`
		if [ ! -f "$texts/$date/$fileName.txt" ]
		then
			pdftotext "$file" "$texts/$date/$fileName.txt" > /dev/null 2>&1
		fi
	done

	# Removes directory containing pdf's
	rm -r "$pdfs/$date"

	echo "Conversion completed and deleted pdf files.\nTxt files are located in the following dir: $texts/$date"

fi

reportNames="gold_drill_results"


# Creates directory for todays reports
if [ ! -d "$reports/$date" ]
then 
	mkdir "$reports/$date"
fi

# Deletes today's reports if they already exists
for name in "$reportNames"
do  
	if [ -f "$reports/$date/$name.txt" ]
	then
		rm "$reports/$date/$name.txt"
	fi
done

# Egrep pattern, creates report
# Might need to delete txt files after use
for file in "$texts/$date/"*
do
	fileName=`echo "$file" | cut -d'/' -f4 | cut -d'.' -f1`
	
	# searches for gold with > 30.0 g/t gold/au (decimal points optional)
	reportName="gold_drill_results"
 	goldDrillResults='(([1-9][1-9]|[ ][3-9])[0-9][ ]?g/t[ ]?(gold|au)|([1-9][1-9]|[ ][3-9])[0-9].[0-9]+[ ]?g/t[ ]?(gold|au))'
	filter="$goldDrillResults"
	# Sends gold_drill_results report to txt file

	if egrep -q -i "$filter" "$file" 
		then
		echo "$fileName\n" >>"$reports/$date/$reportName.txt"
		egrep -i "$goldDrillResults" "$file" >>"$reports/$date/$reportName.txt"
		echo "\n" >>"$reports/$date/$reportName.txt"
	fi



done

count=0

# Prints location of report
for name in "$reportNames"
do
	if [ -f "$reports/$date/$name.txt" ]
	then
		count=$((count + 1))
	fi
done

echo "$count reports created and are located in the following dir:\n'$reports/$date'"