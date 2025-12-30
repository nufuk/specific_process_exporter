#!./venv/bin/python
import time
import psutil
import configparser
import json
from prometheus_client import start_http_server, Gauge, REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR

# TODO 
# prozessnamen aus einem Configfile beziehen, port (logging pfad?), sleeptime
# ordentliche prozess signals wenn das skript beendet wird
# README.MD mit Anleitung
# install.sh um systemctl eintrag erweitern
# gitignore falls nötig erweitern
# Mehr Kommentare


# Standard-Metriken (CPU/Memory des Exporters selbst) entfernen, falls nicht benötigt
[REGISTRY.unregister(c) for c in [PROCESS_COLLECTOR, PLATFORM_COLLECTOR] if c in REGISTRY._collector_to_names]

# Definiere eine Metrik mit Labels für PID und Name
# Wir nutzen den Wert '1', um die Existenz des Prozesses anzuzeigen
process_info = Gauge('process_running_info', 'Info about running processes', ['pid', 'process_name'])

def collect_metrics(process_list):
    # Bestehende Metriken löschen, um tote Prozesse zu entfernen
    found_processes = set()
    process_info.clear()
    for proc in psutil.process_iter(['pid', 'name']):
        pinfo = proc.info
        if not (str(pinfo['name']) in process_list):
            pass
        else:
            try:
                process_info.labels(pid=pinfo['pid'], process_name=pinfo['name']).set(1)
                found_processes.add(pinfo['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    for process_name in process_list:
        if process_name not in found_processes:
            process_info.labels(pid=-1, process_name=process_name).set(0)



if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./config')
    # Starte den Exporter auf dem Port aus der Config
    port = int(config['DEFAULT']['PORT'])
    process_list = json.loads(config.get("DEFAULT","PROCESSES"))
    sleeptimer = int(config['DEFAULT']['SLEEPTIMER'])

    start_http_server(port)
    print(process_list)
    while True:
        collect_metrics(process_list)
        time.sleep(sleeptimer)  # Aktualisierungsintervall