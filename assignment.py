#!/usr/bin/env python

import argparse
from helpers import (create_subnet, create_router, create_server,
                     create_network, add_floating_ip_to_server,
                     destroy_server, destroy_router, destroy_subnet,
                     destroy_network)

ROUTER_NAME = 'nichtj3-rtl'

SUBNET_NAME = 'nichtj3-subnet'
NETWORK_NAME = 'nichtj3-net'
PUBLIC_NETWORK_NAME = 'public-net'

WEB_SERVER = 'nichtj3-web'
APP_SERVER = 'nichtj3-app'
DB_SERVER = 'nichtj3-db'
SERVERS = [WEB_SERVER, APP_SERVER, DB_SERVER]


def create():
    ''' Create a set of Openstack resources '''
    create_network(NETWORK_NAME)
    create_subnet(SUBNET_NAME, NETWORK_NAME)
    create_subnet(SUBNET_NAME, NETWORK_NAME)
    create_router(ROUTER_NAME, SUBNET_NAME, PUBLIC_NETWORK_NAME)
    for server_name in SERVERS:
        create_server(server_name, NETWORK_NAME)
        if(server_name is WEB_SERVER):
            add_floating_ip_to_server(server_name, PUBLIC_NETWORK_NAME)


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
    for server_name in SERVERS:
        destroy_server(server_name)
    destroy_router(ROUTER_NAME, SUBNET_NAME)
    destroy_subnet(SUBNET_NAME)
    destroy_network(NETWORK_NAME)


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
