#!/bin/bash

set -x

. $(dirname $0)/hook_functions.sh

event=${HOOK_EVENT}
object=${HOOK_OBJECT}

hostname=$(hook_data host.name)
rolesnames=$(hook_data host.parameters.value)
ipaddress=$(hook_data host.ip)

filename=/tmp/$hostname
#logfile=/tmp/${0/.sh/}.log
logfile=/tmp/ololo.log

create_file() {
#echo "$rolesnames" > $filename
	echo  "creation du fchier /tmp/$hostname" &>> $logfile
	if [ -f $HOOK_OBJECT_FILE ] ; then
		cp -vf $HOOK_OBJECT_FILE $filename
	else	
		echo  "impossible de trouver le HOOK_OBJECT_FILE : $HOOK_OBJECT_FILE" &>> $logfile
	fi
}

transfert_file() { 
echo  "copie de /tmp/$hostname vers ansible1" &>> $logfile
	if ! /usr/bin/scp  $filename ansible@ansible1:/var/cache/ansible/queues/incoming/ ; then
		echo  "erreur lors de la copie de /tmp/$hostname vers ansible1" &>> $logfile
	fi
}

case $1 in 
	create)
	;;
	update)
	;;
	destroy)
	;;
	before_provision)
		create_file &>> $logfile
		transfert_file  &>> $logfile
	;;
	*)
		echo "Nothing" >> $logfile
	;;
esac
