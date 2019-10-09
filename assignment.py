#!/usr/bin/env
import argparse
import openstack
import utility


conn = openstack.connect(cloud_name='openstack', region_name='nz_wlg_2')

#IMAGE = 'ubuntu-minimal-16.04-x86_64'
NETWORK_NAME = 'zetksm1-net'
SUBNET_NAME = 'zetksm1-subnet'

print("Attempting to create network")

def create():
    ''' Create a set of Openstack resources '''
    try:
    print("Creating network...")    
    network = conn.network.find_network(NETWORK_NAME)
    if network is None:
    network = conn.network.create_network(NETWORK_NAME)
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
