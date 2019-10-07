import argparse
import openstack
import subprocess

def create():
    ''' Create a set of Openstack resources '''
	
	'''network and subnet'''
	subprocess.call(["openstack", "network", "create", "--internal", "schrsa1-net"])
	subprocess.call(["openstack", "subnet", "create", "--network", "schrsa1-net", "--subent-range", "192.168.40.0/24", "schrsa1-subnet"])
	
	'''floating IP'''
	subprocess.call(["openstack", "floating", "ip", "create", "public-net"])
	subprocess.call(["openstack", "floating", "add", "floating", "ip", "schrsa-web", "public-net"])
	
	'''router'''
	subprocess.call(["openstack", "router", "create", "schrsa1-router"])
	subprocess.call(["openstack", "router", "add", "subnet", "schrsa-router", "schrsa1-subnet"])
	subprocess.call(["openstack", "router", "set", "--external-gateway", "public-net", "schrsa1-router"])
	
	'''servers'''
	subprocess.call(["openstack", "server", "create", "--image", "ubuntu-minimal-16.04-x86_64", "--security-group", "assignment2", "--flavor", "c1.c1r1", "--network", "schrsa1-net", "schrsa1-web"])
	subprocess.call(["openstack", "server", "create", "--image", "ubuntu-minimal-16.04-x86_64", "--security-group", "assignment2", "--flavor", "c1.c1r1", "--network", "schrsa1-net", "schrsa1-app"])
	subprocess.call(["openstack", "server", "create", "--image", "ubuntu-minimal-16.04-x86_64", "--security-group", "assignment2", "--flavor", "c1.c1r1", "--network", "schrsa1-net", "schrsa1-db"])
    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
	subprocess.call(["openstack", "server", "start", "schrsa-web"])
	subprocess.call(["openstack", "server", "start", "schrsa-app"])
	subprocess.call(["openstack", "server", "start", "schrsa-db"])
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
	subprocess.call(["openstack", "server", "stop", "schrsa-web"])
	subprocess.call(["openstack", "server", "stop", "schrsa-app"])
	subprocess.call(["openstack", "server", "stop", "schrsa-db"])
    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
	subprocess.call(["openstack", "server", "delete", "schrsa1-db"])
	subprocess.call(["openstack", "server", "delete", "schrsa1-app"])
	subprocess.call(["openstack", "server", "delete", "schrsa1-web"])
	subprocess.call(["openstack", "floating", "ip", "delete", "public-net"])
	subprocess.call(["openstack", "router", "remove", "subnet", "schrsa-router", "schrsa1-subnet"])
	subprocess.call(["openstack", "router", "delete", "schrsa1-router"])
	subprocess.call(["openstack", "subnet", "delete", "schrsa1-subnet"])
	subprocess.call(["openstack", "network", "delete", "schrsa1-net"])
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
	subprocess.call(["openstack", "server", "show", "schrsa1-db"])
	subprocess.call(["openstack", "server", "show", "schrsa1-app"])
	subprocess.call(["openstack", "server", "show", "schrsa1-web"])
    pass


### You should not modify anything below this line ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation',
                        help='One of "create", "run", "stop", "destroy", or "status"')
    args = parser.parse_args()
    operation = args.operation

    operations = {
        'create'  : create,
        'run'     : run,
        'stop'    : stop,
        'destroy' : destroy,
        'status'  : status
        }

    action = operations.get(operation, lambda: print('{}: no such operation'.format(operation)))
    action()