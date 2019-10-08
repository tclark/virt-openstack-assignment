import argparse
import openstack

#  Connect to the openstack service
conn = openstack.connect(cloud_name=’openstack’)

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'clarjc3-net'
ROUTER = 'clarjc3-rtr'
KEYPAIR = 'clarjc3-key'

def create():
    ''' Create a set of Openstack resources '''
    #  Create Network and Subnet
    openstack network create --internal NETWORK
    openstack subnet create --network NETWORK --subnet-range 192.168.50.0/24 clarjc3-subnet
    #  Create Router
    openstack router create ROUTER
    openstack router add subnet ROUTER clarjc3-subnet
    openstack router set --external-gateway public-net ROUTER
    #  Create Server
    
    
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
