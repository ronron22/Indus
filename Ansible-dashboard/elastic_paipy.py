#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
detecté le cas suivant :
foreman réussie, mais ansible ne peut embrayer !!!
"""

from flask import Flask
from flask import render_template
from elasticsearch import Elasticsearch
from libs.es_pai import EsAnsibleCbQuery
import time
from GChartWrapper import Pie
import requests

app = Flask(__name__)


es = Elasticsearch()

espai = EsAnsibleCbQuery()

elastic_host = '213.218.154.197'

def print_all_tasks():
    es_resp = espai.return_tasks_global(elastic_host, 'ansible-deployments-2015', ['_source', 'status', 'msg', 'timestamp', 'stdout', 'bci', 'host', 'cmd', 'Name'], 10)
    all_tasks = []
    # le reversed permet d'affiche les actions les plus récentes à la fin
    for item in reversed(es_resp['hits']['hits']):
        my_timestamp = item['fields']['timestamp'][0] / 1000
        start_date = time.strftime("%d-%m-%Y  %H:%M:%S", time.localtime(int(my_timestamp)))        
        if 'failed' in item['fields']['status'] :
            # on ne récupère pas stdout
            all_tasks.append('<!--failed--> %s - sur <strong> %s</strong> - la  tache <strong>%s</strong> du module <strong>%s</strong> a rencontree l\'erreur suivante : <em>%s</em>' % (start_date, item['fields']['host'][0], item['_source']['invocation']['module_args'], item['_source']['invocation']['module_name'], item['fields']['msg'][0]))
        if 'ok' in item['fields']['status'] :
            all_tasks.append('%s - sur <strong> %s</strong> - la  tache <strong>%s</strong> s\'est correctement executee: %s ' % (start_date, item['fields']['host'][0], item['fields']['Name'][0], item['_source']['invocation']['module_args']))
            #all_tasks.append('%s - sur <strong> %s</strong> - la  tache <strong>%s</strong> du module <strong>%s</strong> s\'est correctement execut&nbsp;e' % (start_date, item['fields']['host'][0], item['_source']['invocation']['module_args'], item['_source']['invocation']['module_name']))

    return all_tasks

def print_failed_tasks():
    es_resp = espai.return_status_global(elastic_host, 'ansible-deployments-2015',  ['_source', '_id', 'status', 'timestamp', 'msg', 'bci', 'host', 'Name'], 10, 'failed')
    nok_tasks = []

    for item in reversed(es_resp['hits']['hits']):
        my_timestamp = item['fields']['timestamp'][0] / 1000
        start_date = time.strftime("%d-%m-%Y  %H:%M:%S", time.localtime(int(my_timestamp)))        
        nok_tasks.append('<!--failed--> %s - sur <strong> %s</strong> - la  tache <strong>%s</strong> du module <strong>%s</strong> a rencontree l\'erreur suivante : <em>%s</em> ' % (start_date, item['fields']['host'][0], item['_source']['invocation']['module_args'], item['_source']['invocation']['module_name'], item['fields']['msg'][0]))
    return nok_tasks

def print_all_tasks_by_type(my_type):
    es_resp = espai.return_tasks_by_type(elastic_host, 'ansible-deployments-2015', ['_source', 'status', 'msg', 'timestamp', 'stdout', 'bci', 'host', 'Name'], 500, my_type)
    all_tasks = []
    # le reversed permet d'affiche les actions les plus récentes à la fin
    for item in reversed(es_resp['hits']['hits']):
        my_timestamp = item['fields']['timestamp'][0] / 1000
        start_date = time.strftime("%d-%m-%Y  %H:%M:%S", time.localtime(int(my_timestamp)))        
        if 'failed' in item['fields']['status'] :
            # on ne récupère pas stdout
            all_tasks.append('<!--failed--> %s - sur <strong> %s</strong> - la  tache <strong>%s</strong> du module <strong>%s</strong> a rencontree l\'erreur suivante : <em>%s</em> ' % (start_date, item['fields']['host'][0], item['_source']['invocation']['module_args'], item['_source']['invocation']['module_name'], item['fields']['msg'][0]))
        if 'ok' in item['fields']['status'] :
            all_tasks.append('%s - sur <strong> %s</strong> - la  tache <strong>%s</strong> du module <strong>%s</strong> s\'est correctement executee' % (start_date, item['fields']['host'][0], item['_source']['invocation']['module_args'], item['_source']['invocation']['module_name']))
    return all_tasks

def print_failed_tasks_by_type(my_type):
    es_resp = espai.return_status_by_type(elastic_host, 'ansible-deployments-2015',  ['_source', '_id', 'status', 'timestamp', 'msg', 'bci', 'host', 'Name'], 50, 'failed', my_type)

    nok_tasks = []
    for item in reversed(es_resp['hits']['hits']):
        my_timestamp = item['fields']['timestamp'][0] / 1000
        start_date = time.strftime("%d-%m-%Y  %H:%M:%S", time.localtime(int(my_timestamp)))        
        nok_tasks.append('<!--failed--> %s - sur <strong> %s</strong> - la  tache <strong>%s</strong> du module <strong>%s</strong> a rencontree l\'erreur suivante : <em>%s</em> ' % (start_date, item['fields']['host'][0], item['_source']['invocation']['module_args'], item['_source']['invocation']['module_name'], item['fields']['msg'][0]))

    return nok_tasks
    
@app.route('/dashboard')
def dashboard():
    all_tasks = print_all_tasks()
    nok_tasks = print_failed_tasks()
    nb_operation = len(all_tasks)
    nb_failed = len(nok_tasks)
    camenbert  = Pie([nb_operation, nb_failed]).title('').color('06921D','red').label('tasks ok', 'tasks nok')
    return render_template('dashboard.html', all_tasks=all_tasks, nok_tasks=nok_tasks, nb_operation=nb_operation, nb_failed=nb_failed, camenbert=camenbert)

@app.route('/dashboard/<server>')
def server_status(server):
    my_type = espai.host_from_type(elastic_host, 'ansible-deployments-2015', server)
    nok_tasks = print_failed_tasks_by_type(my_type)
    all_tasks = print_all_tasks_by_type(my_type)
    nb_operation = len(all_tasks)
    nb_failed = len(nok_tasks)
    camenbert  = Pie([nb_operation, nb_failed]).title('').color('06921D','red').label('tasks ok', 'tasks nok')
    return render_template('dashboard.html', all_tasks=all_tasks, nok_tasks=nok_tasks, server=server, nb_operation=nb_operation, nb_failed=nb_failed, camenbert=camenbert, my_type=my_type)

@app.route('/wtf')
def es_wtf():
    return render_template('wtf.html')

@app.route('/')
def es_index():
    foreman_url = 'foreman1.host.net/api/'
    r = requests.get('https://' + foreman_url + 'hosts?per_page=1000?order=id', auth=('userapi', 'userapi'),verify=False)
    r_dict = r.json()
    list_of_name = []
    for name in r_dict:
        list_of_name.append(name['host']['name'])

    count_foreman_host = len(list_of_name)

    import redis
    r  = redis.client.StrictRedis(host='213.218.154.197')

    delete_list = []
    for host in r.lrange('delete', 0 , -1):
        delete_list.append(host)

    count_paipy_delete_host = len(delete_list)
        
    deferred_list = []
    for host in r.lrange('deferred', 0 , -1):
        deferred_list.append(host) 

    count_paipy_deferred_host = len(deferred_list)

    paipy_camenbert  = Pie([count_paipy_delete_host, count_paipy_deferred_host]).title('').color('06921D','red').label('serveurs ok', 'serveurs nok')

    return render_template('index.html', list_of_name=list_of_name, count_foreman_host=count_foreman_host, delete_list=delete_list, deferred_list=deferred_list, count_paipy_deferred_host=count_paipy_deferred_host, count_paipy_delete_host=count_paipy_delete_host, paipy_camenbert=paipy_camenbert)

@app.route('/help')
def es_help():
    return render_template('help.html')

@app.route('/status')
def pai_status():
    return render_template('pai-status.html')

def new_print_all_tasks():
    es_resp = espai.return_tasks_global(elastic_host, 'ansible-deployments-2015', ['_source', 'status', 'msg', 'timestamp', 'stdout', 'bci', 'host', 'cmd', 'Name'], 200)

    tasks_timestamp = []
    tasks_host = []
    tasks_name = []
    tasks_status = []
    tasks_module = []
    tasks_module_args = []
    tasks_msg = []
    tasks_stdout = []
    
    # le reversed permet d'affiche les actions les plus récentes à la fin
    for item in reversed(es_resp['hits']['hits']):
        my_timestamp = item['fields']['timestamp'][0] / 1000
        start_date = time.strftime("%d-%m-%Y  %H:%M:%S", time.localtime(int(my_timestamp)))        
        tasks_timestamp.append(start_date)
        tasks_host.append(item['fields']['host'][0])
        try:
            tasks_name.append(item['fields']['Name'][0])
        except KeyError:
            tasks_name.append('null')
            pass
        tasks_status.append(item['fields']['status'][0])
        try:
            tasks_module.append(item['_source']['invocation']['module_name'])
        except KeyError:
            tasks_module.append('null')
            pass
        try:
            tasks_module_args.append(item['_source']['invocation']['module_args'])
        except KeyError:
            tasks_module_args.append('null')
            pass
        try:
            tasks_msg.append(item['fields']['msg'][0])
        except KeyError:
            tasks_msg.append('no msg')
            pass
        try:
            tasks_stdout.append(item['fields']['stdout'][0])
        except KeyError:
            #print 'unable to get stdout'
            tasks_stdout.append('no error')
            pass
        
    return  tasks_timestamp, tasks_host, tasks_name, tasks_status, tasks_module, tasks_msg, tasks_stdout, tasks_module_args  

@app.route('/newdashboard')
def newdashboard():
    tasks_timestamp, tasks_host, tasks_name, tasks_status, tasks_module, tasks_msg, tasks_stdout, tasks_module_args = new_print_all_tasks()
    return render_template('newdashboard.html', all_tasks=zip(tasks_timestamp, tasks_host, tasks_name, tasks_status, tasks_module, tasks_msg, tasks_stdout, tasks_module_args))
    #return render_template('newdashboard.html', tasks_name=tasks_name )

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
