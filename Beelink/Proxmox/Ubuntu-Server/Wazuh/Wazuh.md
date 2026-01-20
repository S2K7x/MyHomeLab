# Guide complet – Installation pas à pas de **Wazuh SIEM** sur **Ubuntu 22.04.3 LTS**

## Introduction

Wazuh est une solution **SIEM open-source** puissante permettant :

* la **détection de menaces**
* la **réponse aux incidents**
* la **gestion de la conformité**
* la **supervision de l’intégrité, des logs et des vulnérabilités**

Ce guide couvre **l’installation complète** de Wazuh en mode **All-in-One**, avec :

* Indexer
* Server
* Dashboard
  sur **un seul serveur Ubuntu 22.04.3 LTS**.

---

## Pré-requis

* Ubuntu Server **22.04.3 LTS**
* Accès **root** ou utilisateur avec **sudo**
* Connexion Internet
* Minimum recommandé :

  * 4 CPU
  * 8 Go RAM (16 Go idéal)
  * 50 Go disque

---

## Mise à jour du système

Avant toute chose, mettre à jour l’index APT :

```bash
sudo apt update
```

Passe en root pour éviter les erreurs de permissions :

```bash
sudo su
```

---

## 🚀 Méthode rapide (installation automatisée)

### Installation en une seule commande

```bash
curl -sO https://packages.wazuh.com/4.7/wazuh-install.sh
sudo bash ./wazuh-install.sh -a
```

### Accès à l’interface

* URL :

  ```
  https://<IP_DU_SERVEUR>
  ```
* Identifiants fournis **à la fin de l’installation**

⚠️ **Si le dashboard ne charge pas**
→ manque de ressources (RAM/CPU)
→ augmenter les ressources puis **reboot**

---

## 🧠 Installation manuelle (recommandée pour comprendre Wazuh)

### Architecture Wazuh

Wazuh repose sur **3 composants** :

1. **Indexer**

   * Stockage et indexation des événements (OpenSearch)
2. **Server**

   * Analyse des logs
   * Détection d’attaques
   * Gestion des agents
3. **Dashboard**

   * Interface web
   * Visualisation et investigation

En **All-in-One**, les trois composants sont sur **le même serveur**.

---

## 📁 Préparation de l’environnement

```bash
mkdir wazuh-installer
cd wazuh-installer
```

---

## 1️⃣ Création des certificats TLS

### Téléchargement des scripts

```bash
curl -sO https://packages.wazuh.com/4.7/wazuh-certs-tool.sh
curl -sO https://packages.wazuh.com/4.7/config.yml
```

### Configuration `config.yml`

Remplacer les IP par celles de ton serveur :

```yaml
nodes:
  indexer:
    - name: node-1
      ip: "192.168.251.150"

  server:
    - name: wazuh-1
      ip: "192.168.251.150"

  dashboard:
    - name: dashboard
      ip: "192.168.251.150"
```

### Génération des certificats

```bash
bash ./wazuh-certs-tool.sh -A
```

### Compression

```bash
tar -cvf wazuh-certificates.tar -C wazuh-certificates/ .
rm -rf wazuh-certificates
```

---

## 2️⃣ Installation de l’Indexer

### Dépendances

```bash
apt-get install -y debconf adduser procps gnupg apt-transport-https
```

### Ajout du dépôt Wazuh

```bash
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH \
| gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import

chmod 644 /usr/share/keyrings/wazuh.gpg
```

```bash
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
| tee /etc/apt/sources.list.d/wazuh.list
```

```bash
apt-get update
```

### Installation

```bash
apt-get install -y wazuh-indexer
```

### Déploiement des certificats

```bash
NODE_NAME=node-1
mkdir /etc/wazuh-indexer/certs
tar -xf wazuh-certificates.tar -C /etc/wazuh-indexer/certs/ \
./$NODE_NAME.pem ./$NODE_NAME-key.pem ./admin.pem ./admin-key.pem ./root-ca.pem
```

Permissions :

```bash
chmod 500 /etc/wazuh-indexer/certs
chmod 400 /etc/wazuh-indexer/certs/*
chown -R wazuh-indexer:wazuh-indexer /etc/wazuh-indexer/certs
```

### Démarrage

```bash
systemctl daemon-reload
systemctl enable wazuh-indexer
systemctl start wazuh-indexer
```

Vérification :

```bash
systemctl status wazuh-indexer
```

---

## 3️⃣ Initialisation du cluster

```bash
/usr/share/wazuh-indexer/bin/indexer-security-init.sh
```

Test :

```bash
curl -k -u admin:admin https://192.168.251.150:9200
curl -k -u admin:admin https://192.168.251.150:9200/_cat/nodes?v
```

---

## 4️⃣ Installation du serveur Wazuh

```bash
apt-get install -y wazuh-manager
```

```bash
systemctl enable wazuh-manager
systemctl start wazuh-manager
```

---

## 5️⃣ Installation de Filebeat

```bash
apt-get install -y filebeat
```

Configuration :

```bash
curl -so /etc/filebeat/filebeat.yml \
https://packages.wazuh.com/4.7/tpl/wazuh/filebeat/filebeat.yml
```

Modifier :

```yaml
output.elasticsearch:
  hosts: ["192.168.251.150:9200"]
  protocol: https
  username: ${username}
  password: ${password}
```

Keystore :

```bash
filebeat keystore create
echo admin | filebeat keystore add username --stdin --force
echo admin | filebeat keystore add password --stdin --force
```

Modules :

```bash
curl -s https://packages.wazuh.com/4.x/filebeat/wazuh-filebeat-0.3.tar.gz \
| tar -xvz -C /usr/share/filebeat/module
```

Certificats :

```bash
mkdir /etc/filebeat/certs
tar -xf wazuh-certificates.tar -C /etc/filebeat/certs/ \
./$NODE_NAME.pem ./$NODE_NAME-key.pem ./root-ca.pem
```

Démarrage :

```bash
systemctl enable filebeat
systemctl start filebeat
```

---

## 6️⃣ Installation du Dashboard

```bash
apt-get install -y wazuh-dashboard
```

Configuration :

```yaml
server.host: 0.0.0.0
opensearch.hosts: ["https://192.168.251.150:9200"]
```

Certificats :

```bash
mkdir /etc/wazuh-dashboard/certs
tar -xf wazuh-certificates.tar -C /etc/wazuh-dashboard/certs/ \
./$NODE_NAME.pem ./$NODE_NAME-key.pem ./root-ca.pem
```

Démarrage :

```bash
systemctl enable wazuh-dashboard
systemctl start wazuh-dashboard
```

Accès :

* URL : `https://<IP>`
* User : `admin`
* Pass : `admin`

---

## 🔐 Sécurisation (OBLIGATOIRE)

```bash
/usr/share/wazuh-indexer/plugins/opensearch-security/tools/wazuh-passwords-tool.sh \
--change-all --admin-user wazuh --admin-password wazuh
```

➡️ Stocker les nouveaux mots de passe **immédiatement**.

---

## 👥 Ajout d’agents

### Windows

* Dashboard → Add agent
* Copier la commande PowerShell
* Exécuter en **admin**
* Démarrer le service

### Linux (Ubuntu)

```bash
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
```