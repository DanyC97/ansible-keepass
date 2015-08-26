"""
Store this file as `vars_plugins/password_from_keyring.py` and specify the
following in `ansible.cfg`:
```
    [defaults]
    vars_plugins=./vars_plugins
```
In your inventory specify:
```
[group1]
web[01:99].server.lan
[group1:vars]
x_auth_system="Old Auth Shell User"
[group2]
db[01:10].server.lan
[group2:vars]
x_auth_system="New Auth Shell User"
[shellhosts]
sh01.server.lan
another.server.lan x_auth_system="Standard Shell User"
[all:vars]
ansible_ask_sudo_pass=true
x_auth_system="New Auth Shell User"
```
"""
import getpass
import os
import sys
import libkeepass

class VarsModule(object):

    """
    Loads variables for groups and/or hosts
    """

    def __init__(self, inventory):
        """ constructor """
        self.inventory = inventory
        self.inventory_basedir = inventory.basedir()


    def get_host_vars(self, host, vault_password=None):
        """ Get host specific variables. """
        print "Invoke for %s" % host.name
        if "--ask-su-pass" in sys.argv:
            x_auth_system = host.get_variables().get("x_auth_system")
            ps  = host.get_variables().get("ansible_su_pass")
            if ps is None:
                if x_auth_system == "keepass":
                    # All interesting begins here!
                    rez = {}
                    ps = getpass.getpass(prompt = 'Enter keepass vault password: ')
                    with libkeepass.open( "test.kdbx" , password = ps ) as kdb:
                        for el in kdb.obj_root.findall('.//Entry'):
                            uuid =  el.find('UUID').text
                            rez[uuid] = {}
                            for elem in el.findall('.//String'):
                                key = elem.find('Key').text
                                val = elem.find('Value').text
                                rez[uuid][key] = val
                    for elem in rez.keys():
                        if rez[elem]['Title'] == host.name and rez[elem]['UserName'] == 'root' :
                            passwd = rez[elem]['Password']
#                            print passwd, host.name

                else:
                    raise Exception("Unknown Authentication System %s for host %s" % (x_auth_system, host.name))
                if passwd is None:
                    passwd = getpass.getpass(prompt="%s: su password" % x_auth_system)
                host.set_variable('ansible_su_pass', passwd)