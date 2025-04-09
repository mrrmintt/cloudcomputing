# Image Tag Analyzer

Eine einfache containerbasierte Web-App für die Analyse von Bildern mit Azure Computer Vision API. Dieses Projekt ist Teil eines Cloud Computing-Kurses.

## Projektübersicht

Die Web-App ermöglicht Benutzern das Hochladen von Bildern, die dann mit der Azure Computer Vision API analysiert werden. Die Ergebnisse (Tags, Beschreibungen, erkannte Objekte) werden angezeigt und in einer Azure Cosmos DB gespeichert, um wiederholte Analysen desselben Bildes zu vermeiden.

## Architektur

- **SaaS-Dienst**: Azure Computer Vision API für Bildanalyse
- **PaaS-Dienst**: Azure Cosmos DB (NoSQL) für Datenspeicherung
- **IaaS**: Azure VMs für das Hosting der Anwendung
- **Containerisierung**: Docker
- **IaC**: Terraform für Infrastruktur
- **Konfigurationsmanagement**: Ansible für Deployment und Konfiguration
- **Multi-Region**: Vorbereitet für Deployment in mehreren Azure-Regionen

## Dateien und Komponenten

### Web-App (Flask)
- `app.py`: Hauptanwendungsdatei mit Flask-Routen und Azure-Integration
- `requirements.txt`: Python-Abhängigkeiten
- `Dockerfile`: Container-Definition
- `templates/index.html`: Frontend der Anwendung

### Infrastruktur (Terraform)
- `main.tf`: Haupt-Terraform-Konfiguration für Azure-Ressourcen
- `regions.tf`: Erweiterung für Multi-Region-Deployment

### Deployment (Ansible)
- `playbook.yml`: Ansible-Playbook für App-Deployment
- `inventory.ini`: Ziel-Server-Definition
- `nginx-site.conf.j2`: Nginx-Konfigurationsvorlage
- `deploy.sh`: Automatisiertes Deployment-Skript

## Voraussetzungen

1. Azure-Konto mit Zugriff auf:
   - Azure Computer Vision API
   - Azure Cosmos DB
   - Azure Virtual Machines

2. Installierte Tools:
   - Terraform
   - Ansible
   - Docker (lokal für Tests)

## Setup-Anleitung

### 1. Azure Computer Vision API einrichten

1. Erstelle einen Computer Vision-Ressource im Azure-Portal
2. Notiere dir den API-Schlüssel und Endpunkt

### 2. Terraform-Konfiguration anpassen

1. Stelle sicher, dass du dich bei Azure angemeldet hast (`az login`)
2. Erstelle einen SSH-Schlüssel (`ssh-keygen`) falls noch nicht vorhanden
3. Passe ggf. in `main.tf` die VM-Größe oder andere Parameter an

### 3. Deployment ausführen

```bash
# Berechtigungen für das Deployment-Skript erteilen
chmod +x deploy.sh

# Deployment starten (optional: Region und Präfix angeben)
./deploy.sh westeurope imgtag
```

Das Skript führt folgende Schritte aus:
1. Terraform-Infrastruktur erstellen
2. Ausgaben für Ansible vorbereiten
3. Deployment der Anwendung mit Ansible

### 4. Anwendung verwenden

Nach erfolgreichem Deployment ist die Anwendung unter der IP-Adresse der VM erreichbar. Dort können Bilder hochgeladen und analysiert werden.

## Multi-Region-Deployment

Für ein Multi-Region-Deployment:

1. Passe die `regions.tf`-Datei an und entferne die Kommentare
2. Modifiziere `main.tf`, um Ressourcen pro Region zu erstellen
3. Aktualisiere das Ansible-Inventory, um mehrere Server zu unterstützen

## Fehlerbehebung

- **VM nicht erreichbar**: Prüfe die NSG-Regeln in Azure
- **App startet nicht**: Überprüfe die Logs mit `docker logs image-tag-app`
- **API-Fehler**: Stelle sicher, dass die API-Schlüssel korrekt sind