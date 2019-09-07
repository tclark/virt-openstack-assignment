#!/usr/bin/env


import argparse
import openstack

KEYPAIR = 'sysadminapp'
conn = openstack.connect(could_name='openstack')

NETWORK = "chril2-net"
NETWORK_IP = "192.168.50.0"
NETWORK_MASK = "255.255.255.0"
FLOATING_IP = ""

ROUTER = "chril2-rtl"
SERVERS = ["chrill2-web", "chril2-app", "chril2-db"]
IMAGE = "ubuntu-minimal-1604-x86_64"
FLAVOUR = "c1.c1r1"

def create():
    ''' Create a set of Openstack resources '''
    for server in SERVERS:
        if(conn.compute.find_server(server) == None):
            print(f"Creating server {server}...")
        else:
            print(conn.compute.find_server(server))
            print(f"Server {server} already exists - skipping")
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

