#!/usr/bin/env python
import argparse
import openstack


IMAGE          =  'ubuntu-minimal-16.04-x86_64'
FLAVOR         =  'c1.c1r1'
KEYPAIR        =  'hallmg1-key'
NETWORK        =  'hallmg1-net'
ROUTER         =  'hallmg1-router'
SECURITY_GROUP = ['assignment2']
SERVER_NAMES   = ['hallmg1-web',
                 'hallmg1-app',
                 'hallmg1-db']

conn = openstack.connect(cloud_name='openstack')


def create():
    ''' Create a set of Openstack resources '''
    image   = conn.compute.find_image(IMAGE)
    flavor  = conn.compute.find_flavor(FLAVOR)
    keypair = conn.compute.find_keypair(KEYPAIR)

    # TODO: check if resources already exist before creation
    # TODO: add network and security groups to server creation
    for name in SERVER_NAMES:
        conn.compute.create_server(name=name, image_id=image.id,
                                   flavor_id=flavor.id,
                                   key_name=keypair.name)

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
