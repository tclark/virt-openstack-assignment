import argparse
import openstack
import time

con = openstack.connect(cloud_name="openstack", region_name="nz_hlz_1")
    
IMAGE = "ubuntu-minimal-16.04-x86_64"
FLAVOUR = "c1.c1r1"
NETWORK = "mccacj3-net"
SECURITY_GROUP = "assignment2"
SUBNET = "mccacj3-subnet"
ROUTER = "mccacj3-rtr"
KEYPAIR = "mccacj3-key" 
SERVER_LIST = ['mccacj3-web', 'mccacj3-app', 'mccacj3-db'] 
SUBNET_IP = '192.168.50.0/24'

    
network = conn.network.find_network(NETWORK)
router = conn.network.find_router(ROUTER)
subnet = conn.network.find_subnet(SUBNET)
public_network = conn.network.find_network(PUBLICNET)
image = conn.compute.find_image(IMAGE)
flavour = conn.compute.find_flavor(FLAVOUR)
keypair = conn.compute.find_keypair(KEYPAIR)
    
def create():
    
 
    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
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
