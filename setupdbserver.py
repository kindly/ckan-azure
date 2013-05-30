#! /usr/bin/python
import xml.etree.ElementTree as ET
import base64
import subprocess

tree = ET.parse('/var/lib/waagent/SharedConfig.xml')
root = tree.getroot()

password = base64.b64encode(root.find('Deployment').attrib['guid'])

other_ips = {}

for num, instance in enumerate(root.find('Instances')):
    if num == 0:
        continue
    other_ips[instance.attrib['address']] = False

with open('/etc/postgresql/9.1/main/pg_hba.conf') as hba_read:
    for line in hba_read:
        for key in other_ips:
            if key in line:
                other_ips[key] = True

changed = False
with open('/etc/postgresql/9.1/main/pg_hba.conf', 'a') as hba_append:
    for key, value in other_ips.iteritems():
        if value == False:
             changed = True
             hba_append.write('\nhost    all             all             %s/32            md5' % key)

if changed == True:
    subprocess.call(["sudo", "service", "postgresql", "restart"])


subprocess.call(["sudo", "-u", "postgres", "psql", "-c", "alter user ckan password '%s'" % password])
subprocess.call(["sudo", "-u", "postgres", "psql", "-c", "alter user ckan_datastore_readwrite password '%s'" % password])
subprocess.call(["sudo", "-u", "postgres", "psql", "-c", "alter user ckan_datastore_readonly password '%s'" % password])
