#! /usr/bin/python
import xml.etree.ElementTree as ET
import base64
import sys
import subprocess
import os


def update_config(ip, password):
    os.rename('/etc/ckan/default/production.ini', '/etc/ckan/default/production.ini.old')

    with open('/etc/ckan/default/production.ini.old') as productionold, open('/etc/ckan/default/production.ini', 'w+') as productionew:
        for line in productionold:
            if  line.startswith('sqlalchemy.url'):
                line = 'sqlalchemy.url = postgresql://ckan:%s@%s/ckan\n' % (password, ip)
            if 'ckan.datastore.write_url' in line:
                line = 'ckan.datastore.write_url = postgresql://ckan_datastore_readwrite:%s@%s/ckan_datastore\n' % (password, ip)
            if 'ckan.datastore.read_url' in line:
                line = 'ckan.datastore.read_url = postgresql://ckan_datastore_readonly:%s@%s/ckan_datastore\n' % (password, ip)
            if 'solr_url' in line:
                line = 'solr_url = http://%s:8080/solr \n' % ip
            productionew.write(line)


tree = ET.parse('/var/lib/waagent/SharedConfig.xml')
root = tree.getroot()
password = base64.b64encode(root.find('Deployment').attrib['guid'])

if len(sys.argv) > 1 and sys.argv[1] == "Ready":
    os.remove('/etc/ckan/default/production.ini')
    result = subprocess.call(["/usr/lib/ckan/default/bin/paster", "make-config", "ckan", "/etc/ckan/default/production.ini"])

other_ips = {}
for num, instance in enumerate(root.find('Instances')):
    if num == 0:
        continue
    other_ips[instance.attrib['address']] = False

os.environ['PGPASSWORD'] = password

for key in other_ips:
    result = subprocess.call(["psql", "-h", key, "-U", "ckan", "-c", "select 1"])
    if result == 0:
        result = subprocess.call(["psql", "-h", key, "-U", "ckan", "-c", "select 1 from package"])
        if result == 1:
            update_config(key, password)
            result = subprocess.call(["ckan", "db", "init", "/etc/ckan/default/production.ini"])





