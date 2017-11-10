### Paipy server and client, push to redis foreman build's information and launch Ansible for configuring the vm


* paipy-client.py : pousse sur redis les informations permettant la post-install Ansible
* paipy.py : serveur python gérant la post-install Ansible


## Installation 
```bash
pip install -r requirements
```

#### Howto interact with Redis
incomming, active, delete et deferred sont des "listes" (list) 
l'interet des listes est le classsement dans l'ordre d'arrivé et le pop et push automatique

Ajout manuel d'un serveur :

    redis-cli PUBLISH pai xprimeatb001.host.net

type de d'élément :
 
    type mykey

Composition d'une liste :

    lrange mylist 0 -1

les autres sont des hashs (dict)
l'interet des hashs est l'aspect dictionnaire


Howto redis

Obtenir toutes les clés/valeurs d'un hash (dico)  

    hgetall incomin

Obtenir toutes la valeur d'un clé d'un hash (dico)  

    hget incoming tato.host.net

Supprimer des clés

    del "key name"    

Publier un "host" 

    publish pai toto.host.net 


Pour supprimer toutes les clés :

    flushall

Envoi d'info en pod push :

    publish pai 'pai-test1.host.net 175'


Obtenir les keys présentes dans un zhash :
   
    zrange unreachable 0 -1 withscores 


Pour s'abonner à une queue de pubsub

    subscribe pai

### Foreman API

Foreman API : userapi:*@foreman1.net/api

```bash
[
  {
    "host": {
      "name": "cgpark9.install.net",
      "id": 183,
      "ip": "17.16.1.81",
      "environment_id": 1,
      "environment_name": "production",
      "last_report": null,
      "mac": "00:50:56:9c:4a:99",
      "realm_id": null,
      "realm_name": null,
      "sp_mac": null,
      "sp_ip": null,
      "sp_name": null,
      "domain_id": 2,
      "domain_name": "install.net",
      "architecture_id": 1,
      "architecture_name": "x86_64",
      "operatingsystem_id": 11,
      "operatingsystem_name": "Debian 8.1",
      "subnet_id": 1,
      "subnet_name": "LAN PXE",
      "sp_subnet_id": null,
      "ptable_id": 17,
      "ptable_name": "Debian ptable",
      "medium_id": 2,
      "medium_name": "Debian mirror",
      "build": false,
      "comment": "",
      "disk": "",
      "installed_at": "2015-07-24T12:30:37Z",
      "model_id": 1,
      "model_name": "VMware Virtual Platform",
      "hostgroup_id": 13,
      "hostgroup_name": "Debian 8 ADM 3",
      "owner_id": 13,
      "owner_type": "User",
      "enabled": true,
      "puppet_ca_proxy_id": null,
      "managed": true,
      "use_image": null,
      "image_file": "",
      "uuid": null,
      "compute_resource_id": null,
      "compute_resource_name": null,
      "compute_profile_id": null,
      "compute_profile_name": null,
      "capabilities": [
        "build"
      ],
      "provision_method": "build",
      "puppet_proxy_id": null,
      "certname": "cgpark9.install.net",
      "image_id": null,
      "image_name": null,
      "created_at": "2015-07-24T12:07:35Z",
      "updated_at": "2015-07-24T12:30:38Z",
      "last_compile": null,
      "last_freshcheck": null,
      "serial": null,
      "source_file_id": null,
      "puppet_status": 0,
      "all_puppetclasses": [
      ],
      "parameters": [
      ],
      "interfaces": [
      ],
      "puppetclasses": [
      ],
      "config_groups": [
      ]
    }
  }
]
``` 
