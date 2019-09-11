#!/usr/bin/env python

import argparse
import connection from connection.py

# KEYPAIR = 'sysadminapp'
# SUBNET_NAME = 'nichtj3-subnet'
# SUBNET_IP_VERSION = 4
# SUBNET_CIDR = '192.168.50.0/24'
# NETWORK_NAME = 'nichtj3-net'
# PUBLIC_NETWORK_NAME = 'public-net'

ROUTER_NAME = 'nichtj3-rtl'
SERVERS = ['nichtj3-web', 'nichtj3-app', 'nichtj3-db']
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
SECURITY_GROUP = 'default'


def create():
    ''' Create a set of Openstack resources '''
    pass


def run():
    '''
    Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    pass


def stop():
    '''
    Stop  a set of Openstack virtual machines
    if they are running.
    '''
    pass


def destroy():
    '''
    Tear down the set of Openstack resources
    produced by the create action
    '''
    pass


def status():
    '''
    Print a status report on the OpenStack
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
        'create': create,
        'run': run,
        'stop': stop,
        'destroy': destroy,
        'status': status
    }

    action = operations.get(operation, lambda: print(
        '{}: no such operation'.format(operation)))
    action()
