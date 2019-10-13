#!/usr/bin/env
import argparse
import utility

NETWORK_NAME = 'chril2-net'
SUBNET_NAME = 'chril2-subnet'
PUBLIC_NETWORK_NAME = 'public-net'
ROUTER_NAME = 'chril2-rtl'
SERVER_NAMES = ['chril2-web', 'chril2-app', 'chril2-db']

IMAGE_NAME = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR_NAME = 'c1.c1r1'
SECURITY_GROUP_NAME = 'assignment2'
KEYPAIR_NAME = 'sysadminapp'

SUBNET_IP_VERSION = 4
SUBNET_CIDR = '192.168.50.0/24'


def create():
    ''' Create a set of Openstack resources '''
    utility.create_network(NETWORK_NAME)
    utility.create_subnet(
        SUBNET_NAME, NETWORK_NAME,
        SUBNET_IP_VERSION, SUBNET_CIDR)
    utility.find_public_network(PUBLIC_NETWORK_NAME)
    utility.create_router(
        ROUTER_NAME, PUBLIC_NETWORK_NAME)
    utility.add_interface_to_router(
        ROUTER_NAME, SUBNET_NAME
    )

    for server_name in SERVER_NAMES:
        utility.create_server(
            server_name, IMAGE_NAME, FLAVOUR_NAME,
            KEYPAIR_NAME, SECURITY_GROUP_NAME, NETWORK_NAME)

    utility.add_floating_ip_to_server(
        'chril2-web', PUBLIC_NETWORK_NAME)


def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    for server_name in SERVER_NAMES:
        utility.start_server(server_name)


def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    for server_name in SERVER_NAMES:
        utility.stop_server(server_name)


def destroy():
    ''' Tear down the set of Openstack resources
    produced by the create action
    '''
    for server_name in SERVER_NAMES:
        utility.destroy_server(server_name)

    utility.destroy_router(ROUTER_NAME, SUBNET_NAME)
    utility.destroy_subnet(SUBNET_NAME)
    utility.destroy_network(NETWORK_NAME)


def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    for server_name in SERVER_NAMES:
        utility.get_server_status(server_name)


# You should not modify anything below this line
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
