# Projet Cloud SDN Lab

## Objectif

Mettre en place une infrastructure réseau automatisée avec Vagrant, intégrant :

- Un contrôleur SDN (Ryu + Open vSwitch)
- Deux routeurs dynamiques configurés en OSPF (FRRouting)
- Une automatisation complète avec Ansible
- Injection dynamique des routes dans OpenFlow via Ryu
- Monitoring avec Prometheus + Grafana

---

## Infrastructure

### Machines Virtuelles (via Vagrant)

| Nom        | Rôle              | IP              |
|------------|-------------------|-----------------|
| controller | SDN + Ryu + OVS   | 192.168.56.10   |
| router1    | Routeur OSPF      | 192.168.56.11   |
| router2    | Routeur OSPF      | 192.168.56.12   |

---

## Provisioning

- `Vagrantfile` : Déclaration des VMs et provisioning
- `playbook_ryu.yml` : Installation d'OVS, Ryu, et configuration SDN
- `playbook_frr.yml` : Installation et configuration de FRRouting (OSPF)
- `switch.py` : Script Ryu injectant dynamiquement des règles OpenFlow selon la table de routage système

---

## Tests

### Commandes de vérification :

```bash
# Sur les routeurs
vtysh -c "show ip ospf neighbor"
vtysh -c "show ip route"

# Sur le contrôleur
ovs-vsctl show
ovs-ofctl dump-flows br0
ip route
```

### Ping & connectivité :
```bash
ping 10.0.0.2
```

---

## Monitoring

- Prometheus + Grafana pour la supervision des flux
- Exporters ou NetFlow possibles pour monitorer OSPF et tunnels

---

## Captures attendues

- `ip route`
- `vtysh` (OSPF)
- `ovs-ofctl dump-flows`
- Capture d'écran du schéma réseau (Wireshark ou dessin)

---

## Schéma Réseau

A completer

---

## Auteurs

- Rôle Chef de projet :
- Rôle Architecte Réseau :
- Rôle Intégrateur :
- Rôle DevOps :
- Rédacteur/Documentaliste :

---

## Retour d’expérience

- Problèmes rencontrés :
- Solutions apportées :
- Améliorations possibles :
