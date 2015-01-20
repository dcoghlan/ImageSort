#!/bin/bash

#
# This is the path variable to the folder where you would like to create the new data structure
# and move the files into the new data structure.
var_path=/Users/dcoghlan/Pictures/Google\ Plus/20130513\ -\ 20130731\ -\ Photos

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")


if [ -f "log.txt" ]; then
	rm log.txt
fi

for a in $( ls -F *.gif *.jpg *.mp4 );
	do
	  skip=
	  #var_type=$(echo $a | cut -c 1-6)
	  case "$a" in

          20*\_*\-*)
                # For all normal images edited with Samsung Galaxy S2 Camera
                var_newts=$(echo $a | cut -c 1-8,10-13)

                # extrapolate the directory from the file name
                newdir=$(echo $a | cut -c 1-8)
                newdir_year=$(echo $a | cut -c 1-4)
                ;;

	  20*\-*)
		# For all normal images taken with Samsung Galaxy Y Camera
		#echo "$a" \> SGS2 Image file
	        var_newts=$(echo $a | cut -c 1-4,6-7,9-10,12-13,15-19)

		# extrapolate the directory from the file name
		newdir=$(echo $a | cut -c 1-4,6-7,9-10)
		newdir_year=$(echo $a | cut -c 1-4)
		;;
	  
	  20*\_*)
		# For all images and video taken with Samsung Galaxy S2 Camera
		#echo "$a" \> SGS2 video related file
		var_newts=$(echo $a | cut -c 1-8,10-13)

		# extrapolate the directory from the file name
		newdir=$(echo $a | cut -c 1-8)
		newdir_year=$(echo $a | cut -c 1-4)
	  	;;

	  video\-*.mp4)
		# For all videos taken with Samsung Galaxy Y Camera
		#echo "$a" \> SGY video file
		var_newts=$(echo $a | cut -c 7-10,12-13,15-16,18-19,21-22)

		# extrapolate the directory from the file name
		newdir=$(echo $a | cut -c 7-10,12-13,15-16)
		newdir_year=$(echo $a | cut -c 7-10)
		;;

          IMG\_*.jpg)
                # For all images taken with Instagram Camera on Samsung Galaxy S2
                var_newts=$(echo $a | cut -c 5-12,14-17)

                # extrapolate the directory from the file name
                newdir=$(echo $a | cut -c 5-12)
                newdir_year=$(echo $a | cut -c 5-8)
                ;;

	  *)	
		echo "$a" does not match any patterns | tee -a log.txt
		skip=y
		#echo $skip
	  	;;
	esac
	if [[ "$skip" != "y" ]]; then

		# Update timestamps (modify) on all files
		echo Updating timestamp on "$a"
		touch -m -t "$var_newts" $a

		# check to see if the YEAR directory exists first as a directory, then second as a symbolic link
        	  if [ ! -d "$var_path/$newdir_year" ]; then
        	    if [ ! -L "$var_path/$newdir_year" ]; then

        	      # create the directory if it doesn't exist
        	      echo Creating Directory "$var_path/$newdir_year"
        	      mkdir "$var_path/$newdir_year"

        	    fi
          	fi

          	# check to see if the IMAGE DATE directory exists first as a directory, then second as a symbolic link
          	if [ ! -d "$var_path/$newdir_year/$newdir" ]; then
          	  if [ ! -L "$var_path/$newdir_year/$newdir" ]; then

          	    # create the directory if it doesn't exist
          	    echo Creating Directory "$var_path/$newdir_year/$newdir"
          	    mkdir "$var_path/$newdir_year/$newdir"

          	  fi
          	fi

          	# move files into folder
		echo Moving "$a" to "$var_path/$newdir_year/$newdir/$a"
          	mv $a "$var_path/$newdir_year/$newdir";
	fi
	echo
done

IFS=$SAVEIFS

exit
