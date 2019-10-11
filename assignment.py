#!/usr/bin/env
import argparse
import openstack


conn = openstack.connect(cloud_name='openstack')

#IMAGE = 'ubuntu-minimal-16.04-x86_64'
#FLAVOUR = 'c1.c1r1'
#KEYPAIR = 'zetksm1'
#NETWORK = 'zetksm1-net'
SUBNET_NAME = 'zetksm1-subnet'
IP_VERSION='4'
CIDR='192.168.50.0/24'


#NETWORK_NAME = 'zetksm1_network'

def create():
    ''' Create a set of Openstack resources '''

    network = conn.network.find_network('zetksm1-network')
    if network is None:
        network = conn.network.create_network(name='zetksm1-network')
        print("Network succesfully created")
    else: 
        print("This network already exists")
    

    subnet = conn.network.find_subnet('zetksm1-subnet')
    if subnet is None:
         subnet = conn.network.create_subnet(
         name=SUBNET_NAME,
         network_id=network.id,
         ip_version=IP_VERSION,
         cidr=CIDR
         )
         print("Subnet has been successfully created")
    else:
         print("Subnet has already been created")

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
