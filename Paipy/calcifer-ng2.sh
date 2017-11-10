#!/bin/bash

# Todo #
## critique ##
# revoir le logformat pour declarer les variable local qui ne sont pas récupérés dans les fonctions

set -x

PATH=/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/bin:/usr/local/sbin

\unalias -a

nb_file=2
delay_unreachable_target=3600

playbook_home=/home/ansible/lamp-playbook/
playbook_hostdir=/home/ansible/lamp-playbook/production/
playbook_hosts_vars_dir=/home/ansible/lamp-playbook/host_vars/
playbook_group_vars_dir=/home/ansible/lamp-playbook/group_vars/
scrutation_directory=/var/cache/ansible/queues/
# deferred|active

SCRIPT_NAME=$(basename $0)
LOCK_FILE=/tmp/${SCRIPT_NAME/.sh/}.pid
#LOCK_FILE=/var/run/${SCRIPT_NAME/.sh/}.pid

LOG_FILE=/var/log/calcifer/calcifer.log

LOG_TIMESTAMP="date +%H:%M:%S:%D"
#LOG_INFOS="PPID:$$ PID:$! task number:$nb"
LOG_INFOS="PPID:$$ PID:$! task number:${nb:-n/a}"
LOG_FORMAT="$(${LOG_TIMESTAMP}) $LOG_INFOS"

FOREMAN_USER=userapi
FOREMAN_PASSWD=userapi
FOREMAN_URL=${FOREMAN_USER}:${FOREMAN_PASSWD}@foreman1.ecritel.net/api
CURL_OPTS="-s -f -k -H "Content-Type:application/json" -H "Accept:application/json""

# recuperation du host_group
# curl -k -H "Content-Type:application/json" -H "Accept:application/json"  https://userapi:userapi@foreman1.ecritel.net/api//hostgroups/3
# 2 = Debian Apache ADM3
# 3 = Debian MySQL ADM3
# 4 = Debian Varnish ADM3
# 6 = RH Servers
# 8 = Debian LAMP ADM3
# 9 = Debian ADM3 

# webservers 
# dbservers
# naked_servers
# admn3servers
# webcacheservers

case $* in
	replay)
		for file in $(ls  ${scrutation_directory}deferred/) ; do
			mv -v  ${scrutation_directory}deferred/$file ${scrutation_directory}incoming/
		done
		exit 0
	;;
	list)
		tree --charset=ascii /var/cache/ansible/queues/
		exit 0
	;;
	viewlog)
		tail -n 30  /var/log/{calcifer.log,calcifer2.log}
		exit 0
	;;
	--help|-h)
		echo "replay OR list OR viewlog"
		exit 0
	;;
esac

# on autorise qu'une instance du script
# !!! attention a positionner cette fonction avant l'appel du trap  sinon,
# les fichiers d'active sera copié dans deferred !!!

if [ -f $LOCK_FILE ] ; then
	echo "${LOG_FORMAT} one instance of ${SCRIPT_NAME/.sh/} is already active, exit" | tee -a $LOG_FILE 
	exit 24 ;
else
	echo "$$" > $LOCK_FILE ;
fi

exit_function()
{
	if [ ! -z $NOMOVE ] ; then
		if ! (( $NOMOVE == 1 )) ; then
			for file in $(ls  ${scrutation_directory}active/) ; do
				mv -v  ${scrutation_directory}active/$file ${scrutation_directory}deferred/
			done
		fi
	fi

	if [ -f $LOCK_FILE ] ; then
		rm -f $LOCK_FILE
	else
		echo "${LOG_FORMAT} lock file $LOCK_FILE not found !!!" | tee -a $LOG_FILE
	fi

	if [ -f /tmp/$file ] ; then
		rm -f /tmp/$file
	else
		echo "${LOG_FORMAT} $file not found !!!" | tee -a $LOG_FILE
	fi
	exit 0
}

# on fait le menache en sortant, chi, chi
trap "exit_function" EXIT QUIT TERM


# On blanchi known_hosts 
> /root/.ssh/known_hosts

QUEUE_TREE="deferred active delete incoming"
for queuedir in $QUEUE_TREE ; do
	if [ ! -d $scrutation_directory$queuedir ] ; then
		mkdir $scrutation_directory$queuedir
		chown -R ansible:ansible  $scrutation_directory$queuedir
	fi
done

echo "${LOG_FORMAT} starting scrutation for new elements in ${scrutation_directory}incoming/" | tee -a $LOG_FILE 

incoming2active()
{
	if (( $(ls ${scrutation_directory}incoming/ | wc -l) > 0 )) ; then
		echo -e "\n${LOG_FORMAT}  ==== file(s) found - starting tasks ====" | tee -a $LOG_FILE 
		tree --charset=ascci -t ${scrutation_directory}incoming/ | tee -a $LOG_FILE

		nb=0
		# on itere sur les fichier du repertoire "incoming"
		for file in $(ls -t -1 ${scrutation_directory}incoming) ; do
			nb=$((( $nb+1 )))
			if (( $nb <= $nb_file )) ; then
				echo "${LOG_FORMAT} moving $file in ${scrutation_directory}active/" | tee -a $LOG_FILE
				# on ne force pas l'écrasement d'un fichier existant
				mv -n ${scrutation_directory}incoming/$file ${scrutation_directory}active/
			fi
			 echo -e "${LOG_FORMAT} $nb" | tee -a $LOG_FILE
		done
		tree --charset=ascci -t ${scrutation_directory}active/ | tee -a $LOG_FILE
	else
		echo -e "${LOG_FORMAT} no files, nothing to do, exit normaly\n" | tee -a $LOG_FILE
		exit 0
	fi
}
	
run_tasks()
{
	 nb=0
	for file in $(ls -t -1 ${scrutation_directory}active) ; do
		nb=$((( $nb+1 )))
		# on ne traite pas plus de fichiers que "nb_file"
		if (( $nb <= $nb_file )) ; then
			# on variabilise le role a la lecture du fichier #
			myid=$(jgrep -s  host.hostgroup_id  < ${scrutation_directory}active/$file)
			# on verifie qu'un id est present sinon tous les roles son chargés
			if [ ! -z $myid ] ; then
				if ! curl -f -k -H "Content-Type:application/json" -H "Accept:application/json" https://userapi:userapi@foreman1.ecritel.net/api/hostgroups/${myid} > /tmp/$file ; then 
					echo "${LOG_FORMAT} unable to get the hostgroups id on foreman1.ecritel.net/api/" | tee -a $LOG_FILE
				else
					echo "${LOG_FORMAT} getting hostgroups id on foreman1.ecritel.net/api/ ok" | tee -a $LOG_FILE
				fi
				if [ ! -f /tmp/$file ] ; then
					echo "${LOG_FORMAT} unable to read /tmp/$file for getting the hostgroup.parameters.roles" | tee -a $LOG_FILE
				else	
					roles=$(jgrep -s hostgroup.parameters.roles < /tmp/$file)
					echo "${LOG_FORMAT} getting $roles roles" | tee -a $LOG_FILE
				fi
			fi

			# on extrait l'environnement (localisation) 
			env_id=$(jgrep -s  host.environment_id < ${scrutation_directory}active/$file)
			echo "${LOG_FORMAT} setting $env_id " | tee -a $LOG_FILE
			env_json=$(curl $CURL_OPTS https://$FOREMAN_URL/environments/${env_id})
			echo "${LOG_FORMAT} setting $env_json " | tee -a $LOG_FILE
			env_value=$(echo "$env_json" |jgrep -s environment.name)
			echo "${LOG_FORMAT} setting $env_value for localisation " | tee -a $LOG_FILE

			# on extrait l'utilisateur 
			user_id=$(jgrep -s host.owner_id < ${scrutation_directory}active/$file)
			echo "${LOG_FORMAT} setting $user_id" | tee -a $LOG_FILE
			user_json=$(curl $CURL_OPTS https://$FOREMAN_URL/users/${user_id})
			user_value=$(echo "$user_json" |jgrep -s user.login)
			echo "${LOG_FORMAT} setting $user_value " | tee -a $LOG_FILE
			
			echo "${LOG_FORMAT} task number:${nb:-n/a} loading $file" | tee -a $LOG_FILE
		
			# on blanchi le fichier
			echo "${LOG_FORMAT} task number:${nb:-n/a} wipping of ${playbook_hostdir}host-$file" | tee -a $LOG_FILE
			> ${playbook_hostdir}host-$file

			# on ajoute l'utilisateur
			echo "# installed by $user_value" >> ${playbook_hostdir}host-$file

			if [ ! -f ${playbook_hosts_vars_dir}$file ] ; then
				echo -e "${LOG_FORMAT} host_vars file not found for $file" | tee -a $LOG_FILE
			else
				echo -e "${LOG_FORMAT} host_vars file found $file" | tee -a $LOG_FILE
			fi

			#if ! -f ${playbook_group_vars_dir}$file ; then
			#	echo -e "${LOG_FORMAT} group_vars file not found" | tee -a $LOG_FILE
			#else
			#	echo -e "${LOG_FORMAT} group_vars file found" | tee -a $LOG_FILE
			#fi

			if [ ! -z "$roles" ] ; then
				# 2.0 : on itère sur les roles pour les inserer dans le fichier host-*
				for role in $roles ; do
					# role 1.0 : si le role n'est pas defini
					echo -e "[$role]\n${file} site_name=$env_value ansible_ssh_user=root proxy_on=pouet" >> ${playbook_hostdir}host-$file 
				done
			else	
				echo -e "${LOG_FORMAT} task number:${nb:-N/A} no role found for ${playbook_hostdir}host-$file" | tee -a $LOG_FILE
				# role 1.1 : seule les roles common et endtask seront appliqués
				echo -e "${file} ansible_ssh_user=root proxy_on=pouet" >> ${playbook_hostdir}host-$file 
			fi

			# on test la connectvité réseau
			# la valeur laisse le temps a ssh de démarrer 
			if fping -c 30 -q ${file} ; then
				echo "${LOG_FORMAT} task number:${nb:-n/a} ${file} is reached, running playbook now" | tee -a $LOG_FILE
				{ ansible-playbook --private-key=/home/ansible/.ssh/install -i ${playbook_hostdir}host-$file ${playbook_home}site.yml ;  echo "$file $?" >> $LOCK_FILE ; } &
				echo "${LOG_FORMAT} task number:${nb:-n/a} launch of $! for ${file}" | tee -a $LOG_FILE
			else
				if [ ! -f ${scrutation_directory}active/${file} ] ; then
					echo "${LOG_FORMAT} file ${scrutation_directory}active/$file not exist" | tee -a $LOG_FILE
				else
					if (( ($(date  +%s) - $(stat --format "%Y" ${scrutation_directory}active/${file} )) > $delay_unreachable_target )) ; then 
						echo "${LOG_FORMAT} host is unreachable for to long time $file" | tee -a $LOG_FILE
						echo "${LOG_FORMAT} moving ${scrutation_directory}active/$file on ${scrutation_directory}deferred/" | tee -a $LOG_FILE
						mv -v ${scrutation_directory}active/$file ${scrutation_directory}deferred/
					else
						echo "${LOG_FORMAT} task number:${nb:-n/a} ${file} is unreachable, requeued ..." | tee -a $LOG_FILE
						mv -n ${scrutation_directory}active/$file ${scrutation_directory}incoming/
					fi
				fi	
				export NOMOVE=1
				# on passe à l'itération suivante
				continue
			fi
		fi
		echo "${LOG_FORMAT} task number:${nb:-n/a} iteration suivante ou finale" | tee -a $LOG_FILE
	done

		echo "${LOG_FORMAT} fin de boucle" | tee -a $LOG_FILE
		echo "${LOG_FORMAT} jobs are $(jobs -p)" | tee -a $LOG_FILE
	wait
	echo "${LOG_FORMAT} fin du wait" | tee -a $LOG_FILE
}

active2other()
{
	## return code verification ##
	nb=0
	cat $LOCK_FILE
	while read line ; do 
		nb=$((( $nb+1 )))
		echo $nb
		if (( $nb == 1 )) ; then	
			continue
		else
			echo $line | tee -a $LOG_FILE
			file="${line%%" "*}"
			if (( ${line##*" "} > 0 )) ; then
				echo "${LOG_FORMAT} error on runing playbook for $file" | tee -a $LOG_FILE
				echo "${LOG_FORMAT} moving ${scrutation_directory}active/$file on ${scrutation_directory}deferred/" | tee -a $LOG_FILE
				mv -v ${scrutation_directory}active/$file ${scrutation_directory}deferred/
			else
				echo "${LOG_FORMAT} moving ${scrutation_directory}active/$file on ${scrutation_directory}delete/" | tee -a $LOG_FILE
				mv -v ${scrutation_directory}active/$file ${scrutation_directory}delete/
			fi
		fi
	done < $LOCK_FILE

	echo "${LOG_FORMAT} ==== end tasks ====" | tee -a $LOG_FILE 
}		
	
incoming2active

run_tasks

active2other
