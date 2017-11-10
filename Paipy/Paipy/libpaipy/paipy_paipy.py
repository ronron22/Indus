#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import requests
import json
import os
#import logging
#from logging.handlers import RotatingFileHandler

#logger2 = logging.getLogger()
#logger2.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
#file_handler2 = RotatingFileHandler('/var/log/paipy/paipy.log', 'a', 1000000, 1)

#file_handler2.setLevel(logging.DEBUG)
#file_handler2.setFormatter(formatter)
#logger2.addHandler(file_handler2)

class PaipyLib:

    def hosts_resolv(self, host_name):

        self.host_name = host_name
        
        host_resolved = []
        
        try:
            socket.gethostbyname(self.host_name)
        except:
            host_resolved.append('')
        host_resolved.append(self.host_name)
        return host_resolved

    def netprobe(self, host_name, nb):

        self.host_name = host_name
        self.nb = nb
        
        host_reachable = []
        
        response = os.system('ping -c %s %s &>> /var/log/paipy/paipy.log' % (self.nb, self.host_name))
        if response == 0:
            host_reachable.append(self.host_name)
        else:
            host_reachable.append('')
        return host_reachable
    

    def loadjsonhost(self, url, host_vars, hash_name, nb, host):

        """
        Ici, on récupère quelques éléments de l'API foreman et on les associes à un
        hash représenté par le nom du hosts
        éléments récupérés :
        'hostgroup_id',
        'environment_name',
        'ip',
        'name',
        'created_at',
        'hostgroup_name',
        'operatingsystem_name',
        'parameters',
        'mac',
        'owner_id',
        'build',
        """

        """
        url : https://userapi:userapi@foreman1.net/
        host_id: 175 
        host_var : liste de variables
        hash_name = nom du hash duquel sont extraites les keys 'active'
        """

        self.url = url
        self.host_vars = host_vars 
        self.hash_name = hash_name
        self.nb = nb
        self.host = host
		
        # pour chacun des 2 hosts on instancie une requête vers foreman
        r1 = requests.get((self.url+'api/v2/hosts/'+self.host), verify=False)
        # pour chaque élément de la liste host_vars
        host = self.host
        host = {}
        for elem in self.host_vars:
            # on créé une variable avec la valeur de l'élement
            # en interrogeant le dict json
            b = r1.json()[elem]
            #print elem
            #print b

            """
            Achtung !!!
            le cas de 'parameter' est différent, il s'agit d'une liste insérée
            dans le dict json de request, impossible donc d'interroger unitairement
            ses éléments 
            """

            if 'parameters' in elem:
                b = r1.json()[elem]
                # on charge la liste en json, cela devient une 'str' 
                b = json.dumps(b)
                # si la 'liste' n'est pas vide
                if '[]' not in b:
                    print('b existe ici')
                    # on transforme b en dict json
                    y = json.loads(b)[0]
                    # et enfin on extrait le nom
                    name = y['name']
                    #print 'name: '+name
                    # et on l'insère dans le hash de l'host
                    
                    host['mon cul']=name 
                else:
                    print('b existe po')

            if 'hostgroup_id' in elem:
                r2 = requests.get(self.url+'api/hostgroups/'+str(b), verify=False)
                my_roles_names = r2.json()['hostgroup']['parameters']['roles']
                host['role']=my_roles_names

            host[elem]=b

        return  host
        


    def inventory_host_formating(self, file_name, host, roles, *args, **kwargs):

        self.file_name = file_name+host
        self.roles = roles
        self.host = host      

        extra_vars = ''
        for i in args :
            extra_vars += i 

        f = open(self.file_name, 'w')
        print('writing inventory file for %s with : %s, %s' % (host, roles, extra_vars)) 
        for role in self.roles.split():
            f.write('[%s]\n%s %s\n' % (role, self.host, extra_vars))

        f.close()
