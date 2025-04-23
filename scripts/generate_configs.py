
# Jinja2 will generate server configs for Prometheus, Alertmanager, and Ansible using the newly provisioned server IPs.
#
# ------------------------------------------------------------------------------------------------------------------
#
# Usage: python3 generate_configs.py <command> <args>
#
#
# Example: Generate Prometheus config file
#   - python3 generate_configs.py gp <nginx_server_ip>

# Example: Generate Alertmanager config file
#   - python3 generate_configs.py gam <ansible_server_ip>

# Example: Generate Ansible inventory file
#   - python3 generate_configs.py gan <nginx_server_ip>

# Example: Generate all configs
#   - python3 generate_configs.py gall <nginx_server_ip> <ansible_server_ip>
#

import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from typing import Optional
from typer import Typer, Argument
from loguru import logger

app = Typer()

parentdir = Path(__file__).resolve().parent.parent
pathprometheus = Path(f'{parentdir}/prometheus/config').resolve()
pathansible = Path(f'{parentdir}/ansible/config').resolve()

@app.command()
# Write a help message for the command
def gp(nginx_server: str = Argument(..., help="Generate the Prometheus config: nginx_server=<nginx_server_ip>")):
    """
    Generate the Prometheus Config File (prometheus.yml) for the Prometheus server.
    [params: nginx_server: IP address of the Nginx server]
    """
    env = Environment(loader=FileSystemLoader('jinja'))

    # Load template files
    prometheus_template = env.get_template('prometheus.yml.j2')

    rendered_prometheus = prometheus_template.render(nginx_server=nginx_server)

    # Save rendered templates to files

    with open(f'{pathprometheus}/prometheus.yml', 'w') as f:
        f.write(rendered_prometheus)
    logger.info(f'Prometheus config generated prometheus/config/prometheus.yml: {nginx_server}')

@app.command()
def gam(ansible_server: str = Argument(..., help="Generate the Alertmanager config: ansible_server=<ansible_server_ip>")):
    """
    Generate the Alertmanager Config File (alertmanager.yml) for the Alertmanager server.
    [params: ansible_server: IP address of the Ansible server]
    """
    env = Environment(loader=FileSystemLoader('jinja'))

    # Load template files
    alertmanager_template = env.get_template('alertmanager.yml.j2')

    rendered_alertmanager = alertmanager_template.render(ansible_server=ansible_server)

    # Save rendered templates to files

    with open(f'{pathprometheus}/alertmanager.yml', 'w') as f:
        f.write(rendered_alertmanager)
    logger.info(f'Alertmanager config generated prometheus/config/alertmanager.yml: {ansible_server}')

@app.command()
def gan(nginx_server: str = Argument(..., help="Generate the Ansible Inventory File: ansible_server=<ansible_server_ip>")):
    """
    Generate the Ansible Inventory File (inventory.ini) for the Ansible server.
    [params: ansible_server: IP address of the Ansible server]
    """
    env = Environment(loader=FileSystemLoader('jinja'))

    # Load template files
    inventory_template = env.get_template('inventory.ini.j2')

    rendered_inventory = inventory_template.render(nginx_server=nginx_server)

    # Save rendered templates to files

    with open(f'{pathansible}/inventory.ini', 'w') as f:
        f.write(rendered_inventory)
    logger.info(f'Ansible inventory file generated ansible/config/inventory.ini: {nginx_server}')

@app.command()
def gall(
    nginx_server: str = Argument(..., help="Generate the Prometheus config: nginx_server=<nginx_server>"), 
    ansible_server: str = Argument(..., help="Generate the Alertmanager config: ansible_server=<ansible_server>")
):
    """
    Generate All Configs: Prometheus(prometheus.yml), Alertmanager(alertmanager.yml), and Ansible inventory file(inventory.ini).
    [params: nginx_server: IP address of the Nginx server, ansible_server: IP address of the Ansible server]
    """
    gp(nginx_server)
    gam(ansible_server)
    gan(nginx_server)
    logger.info(f'All configs generated.')

if __name__ == '__main__':
    app()