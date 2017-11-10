@startuml

== Définition de l'host ==

Utilisateur -> Vcenter: Création de la VM (et récupération de l'adresse mac)
Utilisateur --> Foreman: Création de l'host (avec l'adresse mac)
Utilisateur --> Ansible: Définition des variables dans /home/ansible/ansible/host_vars/ (optionnel)

== Début installation système ==

Utilisateur --> Vcenter: Boot de la VM sur le PXE
/'Foreman --> Host: Installation du système'/
Host --> Host: Reboot automatique de la VM

== Début post-configuration  ==

Utilisateur --> Ansible_Dashboard: Suivie de l'éxecution de la post-configuration
/'Foreman --> Olalala : Exécution du hooks
Olalala --> Paipy_client: Appel de paipy_client
Paipy_client --> Redis: Ajout host dans le Pub/Sub Redis de scheduler1
Paipy_serveur <-- Redis: récupération de la nouvelle clé'/
Paipy_serveur --> Ansible: Ordonnancement et exécution du playbook
Ansible --> Host: Déroulement du playbook
/'Ansible --> Scheduler1: Injection des logs dans Elasticsearch (via le callback)
Ansible <-- Gitlab: Récupération des configurations et templates'/
Ansible --> Host: Reboot automatique de la VM

@enduml
