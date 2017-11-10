#!/usr/bin/python
# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch

"""
Pensez à soumettre des listes de 'fields' au fonction de recherche exemple :
	pouet = myobj.search_status('localhost', 'ansible-deployments-2015',  ['status', 'msg'], 'failed')

"""


class EsAnsibleCbQuery:

    def __init__(self):
	pass

    def return_status_global(self, host, index, fields, size, status_name):

        """
	    cette méthode permet d'obtenir les tasks en status 'ok' ou 'failed'

	    Pour obtenir les sequences en erreur :
	    tasks_err = myobj.search_status('localhost', 'ansible-deployments-2015', ['status', 'msg'], 'failed') 
	    Pour obtenir les sequences ok :
	    tasks_ok = myobj.search_status('localhost', 'ansible-deployments-2015', ['status', 'msg'], 'ok')

	    Cette méthode devrait être utilisé avec les 'fields' :
	    - status
	    - msg 
	    """

        self.host = host
        self.index = index
        self.fields = fields
        self.size = size
        self.status_name = status_name

    	#for field in self.fields.split():
	    #	self.fields.append(field)

	    # on ouvre la connexion
        es = Elasticsearch(host)
    
        tasks_list = es.search(
            index=self.index, body={
                "fields" : self.fields, "size" : self.size, "query": {
                    "match": {
                        "status": self.status_name}}})
    	return  tasks_list


    def return_tasks_global(self, host, index, fields, size):

        """
	    cette méthode renvoi les 'size' dernières tasks' :
	    - trier ordre descendant sur le champs 'timestamp' (les plus récent en premier)

	    Cette méthode devrait être utilisé avec les 'fields' :
	    - status
	    - msg 
	    - stdout
	    - module_args
	    """

        self.host = host
        self.index = index
        self.fields = fields
        self.size = size

        # on ouvre la connexion
        es = Elasticsearch(host)

        all_tasks_list = es.search(
            index=self.index, body={
                 "fields" : self.fields ,"size" : self.size, "sort" : [{
                     "timestamp" : {
                        "order" : "desc"} }, ], "query": {
                        "match_all": {
                    }}})
    	return  all_tasks_list

    def host_from_type(self, host, index, server):
    
        """
	    cette méthode permet de retrouver toutes 
        les sequences rattachées à un serveur,
        en se basant sur le _type qui est la "clé
        primaire" du sequence
        """  

        self.host = host
        self.index = index
        self.server = server

        # on ouvre la connexion
        es = Elasticsearch(host)

        json_type = es.search(
            index=self.index, body={
                "fields" : ["_type"] , "size" : 1, "sort" : [{"_type" : { "order" : "desc"}},],  "query": {
                    "match": {
                         "host": self.server}}})
        type_value = json_type['hits']['hits'][0]['_type']

        return type_value

    def return_status_by_type(self, host, index, fields, size, status_name, type_value):

        """
	    cette méthode permet d'obtenir les tasks en status 'ok' ou 'failed' pour un host donné
        en argument.
	    Pour obtenir les sequences en erreur :
        spai.return_status('localhost', 'ansible-deployments-2015',  ['status', 'msg', 'bci'], 50, 'failed', my_type)
        ou 'my_type' est le resultat de la méthode "host_from_type"

	    Cette méthode devrait être utilisé avec les 'fields' :
	    - status
	    - msg 
	    """

        self.host = host
        self.index = index
        self.fields = fields
        self.size = size
        self.status_name = status_name
        self.type_value = type_value

	    # on ouvre la connexion
        es = Elasticsearch(host)
    
        tasks_list = es.search(
            index=self.index, body={
                "fields" : self.fields, "size" : self.size, "query": {
                    "bool": {
                        "must": [{
                            "term": {
                                "status": self.status_name
                                    }
                                }, 
                                {
                                    "term": {
                                        "_type": self.type_value 
                                            }
                                }]
                            ,"minimum_should_match" : 2, 
                        }
                    }
                })
    	return  tasks_list


    def return_tasks_by_type(self, host, index, fields, size, type_value):

        """
	    cette méthode permet d'obtenir toutes les tasks  pour un host donné
        en argument.

        'my_type' est le resultat de la méthode "host_from_type"

	    Cette méthode devrait être utilisé avec les 'fields' :
	    - status
	    - msg 
	    """

        self.host = host
        self.index = index
        self.fields = fields
        self.size = size
        self.type_value = type_value

	    # on ouvre la connexion
        es = Elasticsearch(host)
    
        all_tasks_list = es.search(
            index=self.index, body={
                 "fields" : self.fields ,"size" : self.size, "sort" : [{
                     "timestamp" : {
                        "order" : "desc"} }, ], "query": {
                        "term": { "_type": self.type_value }
                }})
    	return  all_tasks_list
