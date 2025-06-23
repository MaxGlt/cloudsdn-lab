# Projet Cloud SDN Lab

## Objectif

Concevoir et déployer une infrastructure réseau virtualisée complète, incluant :

- Un contrôleur SDN (Ryu + Open vSwitch)
- Deux routeurs dynamiques avec OSPF (FRRouting)
- Une automatisation complète via Vagrant + Ansible
- Une injection automatique de règles OpenFlow selon les routes OSPF
- Un monitoring réseau avec Prometheus + Grafana

---

## Infrastructure

### Machines virtuelles (Vagrant)

| Nom        | Rôle                    | Réseaux / IPs                         |
|------------|-------------------------|----------------------------------------|
| `controller` | SDN Controller (Ryu + OVS) | `192.168.56.10` + interfaces OVS sans IP |
| `router1`   | Routeur OSPF + Client 1     | `192.168.56.11`, `10.0.0.2`, `192.168.10.254` |
| `router2`   | Routeur OSPF + Client 2     | `192.168.56.12`, `10.0.1.2`, `192.168.20.254` |
| `client1`   | Hôte client 1              | `192.168.10.2`                         |
| `client2`   | Hôte client 2              | `192.168.20.2`                         |
| `monitoring` (optionnel) | Grafana + Prometheus | `192.168.56.13`                      |

---

## Provisioning (automatisé)

| Composant              | Playbook / Script                           |
|------------------------|---------------------------------------------|
| VMs + réseaux          | `Vagrantfile`                               |
| Ryu + OVS              | `playbook_ryu.yml`, `switch.py`             |
| Routeurs OSPF (FRR)    | `playbook_frr.yml`, `playbook_interfaces.yml` |
| Exporters Prometheus   | `playbook_node-exporter.yml`, `playbook_ospf-exporter.yml` |
| Monitoring             | `playbook_monitoring.yml` |

---

## Tests & vérifications

### Connectivité réseau

```bash
# Depuis router1
ping 10.0.0.2       # loopback test
ping 192.168.10.2   # client1

# Depuis router2
ping 10.0.1.2       # loopback test
ping 192.168.20.2   # client1

# Depuis controller
sudo ovs-vsctl show
sudo ovs-ofctl dump-flows br0
```

### FRRouting (vtysh)

```bash
sudo vtysh -c "show ip ospf neighbor"
sudo vtysh -c "show ip route ospf"
sudo vtysh -c "show ip route"
sudo vtysh -c "show ip ospf database"
sudo vtysh -c "show running-config"
```

### OpenFlow (Ryu)

```bash
sudo ovs-ofctl dump-flows br0
sudo systemctl status ryu
sudo tail -f /var/log/syslog | grep ryu
```

### Monitoring

### [Accès Grafana](http://localhost:3000)

1. Informations d'identification :
  - User : admin
  - Password : admin

2. Cliquer sur Skip

### [Accès Prometheus](http://localhost:9090)

## Schéma Réseau

À compléter : inclure topologie SDN, plan d’adressage, et flux OSPF + OpenFlow

---

## Équipe projet

| Rôle                 | Nom                       |
|----------------------|---------------------------|
| Chef de projet       | ...                       |
| Architecte réseau    | ...                       |
| Intégrateur Ansible  | ...                       |
| DevOps               | ...                       |
| Rédacteur technique  | ...                       |

---

## Retour d’expérience

### Problèmes rencontrés

- Interfaces VirtualBox non détectées → résolu avec `auto_config: false`
- Besoin d'IP statiques pour OSPF inter-VMs

### Solutions apportées

- Utilisation de `intnet` + IP statique via Ansible
- Port OVS configuré sans IP côté controller

## Structure du dépôt

```
.
├── ansible
│   ├── files
│   │   ├── 1860_rev41.json
│   │   ├── frr_ospf_exporter.py
│   │   ├── prometheus.yml
│   │   ├── requirements.txt
│   │   ├── ryu.service
│   │   └── switch.py
│   ├── inventory.ini
│   ├── playbook_client.yml
│   ├── playbook_frr.yml
│   ├── playbook_interfaces.yml
│   ├── playbook_monitoring.yml
│   ├── playbook_node-exporter.yml
│   ├── playbook_ospf-exporter.yml
│   ├── playbook_ryu.yml
│   └── templates
│       ├── frr.conf.j2
│       ├── interfaces_router1.j2
│       └── interfaces_router2.j2
├── README.md
└── Vagrantfile
```

---

## Lancement

```bash
vagrant up
```