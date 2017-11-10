# Foreman tools

## mécanisme de hook Foreman

résumé court : hook_functions.sh donne accès à la fonction hook_data qui permet de parser facilement l'objet json créé par le hook Foreman.

Explications confuses :

hook_functions.sh créé, dans /tmp/, un objet json contenant la définition d'un host

lors de son appel, la variable HOOK_EVENT prend le nom de l'event de création ex "before_provision", la variable HOOK_OBJECT prend elle, le fqdn de l'objet ex "toto2.ecritel.net". 

Lorsque l'on source hook_functions.sh ". $(dirname $0)/hook_functions.sh", on peut appeler la fonction hook_data qui prend en argument un index du json ex :

     hostname=$(hook_data host.name)

Entraine un 

    jgrep -s "$1" < $HOOK_OBJECT_FILE




## Adaptation pour Ansible dans le cadre PAI 


### descriptif de calcifer :

Il s'agit d'un ordonanceur se basant sur une hierarchie "physique" de répertoires ou chacun de ces derniers représente un état de la file d'attente, par exemple :

* deferred, répertoire accueillant les traitements en erreurs
* incoming, répertoire accueillant les fichiers à traiter
* deleted, répertoire accueillant les traitements terminés sans erreurs
* active, répertoire accueillant les traitements à effectuer ou s'effetuant


l'ordonanceur s'assure qu'un "host" ne soit jamais présent dans plus d'un répertoire.

Cette structure lui donne une grande clarté et une bonne robustesse.

"Inspiré de la hierarchie de Postfix"


### Fonctionnement :

1. calcifer scrute toutes les 5 minutes si un fichier est arrivé dans "incoming" 
2. un message arrive par scp et est déposé dans "incoming"
3. les messages trouvés sont déplacés dans "active", 2 par période de 5 mn, dans la logique FIFO 
4. on extrait le "hostgroup" associé au serveur
5. à partir du "hostgroup" on extrait les rôles associés
6. on extrait le "host.environment_id" associé au serveur
7. à partir du "host.environment_id" on obtient la localisation du serveur 
8. on extrait le "host.owner_id" associé au serveur
9. à partir du "host.owner_id" on obtient l'installateur du serveur
10. on blanchi un éventuel fichier d'inventaire Ansible
11. si un éventuel fichier "host_vars" existe on charge les variables 
12. si un éventuel fichier "group_vars" existe on charge les variables 
13. on "forge" un fichier d'inventaire en insèrant les rôles
14. on tente de pinguer le serveur pendant 30 secondes puis, en cas de réussite, on lance le playbook Ansible
15. si le serveur ne répond pas au ping, on le remet dans "incoming"  mais si le fichier à plus d'une heure, on le bascule dans la file "deferred" 
16. on attend la fin de l'executin du playbook
17. si le playbook s'est bien déroulé, le fichier est copié dans "deleted" sinon, il ira dans "deferred"





