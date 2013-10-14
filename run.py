import subprocess
import random
import string
import sys

if len(sys.argv) != 4:
    print 'run username vmname cert'
    sys.exit(1)

password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(70)) + '?'

user, name, cert = sys.argv[1], sys.argv[2], sys.argv[3]

subprocess.call(
["azure",  "vm",  "create",  name, "-o", "vmdepot-1398-1-32",  user, password, "-n", name + "db" , "-e", "50022", "-t", cert, "--location", "West Europe"]
)

subprocess.call(
["azure",  "vm",  "create",  name, "-o", "vmdepot-1397-1-32", user, password, "-n", name + "web", "-e", "-t", cert, "--location", "West Europe", "-c"]
)

subprocess.call(
["azure", "vm", "endpoint", "create", name+"web", "80", "80"]
)



