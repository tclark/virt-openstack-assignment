#!/usr/bin/env
import argparse
import utilities

NETWORK_NAME = 'chril2-net'
SUBNET_NAME = 'chril2-subnet'
PUBLIC_NETWORK_NAME = 'public-net'
ROUTER_NAME = 'chril2-rtl'
SERVER_NAMES = ['chril2-web', 'chril2-app', 'chril2-db']

def create():
    ''' Create a set of Openstack resources '''
    network = utilities.create_network(NETWORK_NAME)
    subnet = utilities.create_subnet(SUBNET_NAME, network)
    public_net = utilities.find_public_network(PUBLIC_NETWORK_NAME)
    utilities.create_router(ROUTER_NAME, subnet, public_net)
    for server_name in SERVER_NAMES:
        utilities.create_server(server_name, network)
        if(server_name == 'chril2-web'):
            utilities.add_floating_ip_to_server(server_name, public_net)

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    ''' 
    for server_name in SERVERS:
        server = conn.compute.find_server(server_name)
        if(server == None):
            print(f'\nServer {server_name} does not exist. To create it, run this script with the create option.')
        else:
            print(f'\nStarting server {server_name}...')
            conn.compute.start_server(server)

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    for server_name in SERVER_NAMES:
        server = conn.compute.find_server(server_name)
        if(server == None):
            print(f'\nServer {server_name} does not exist. To create it, run this script with the create option.')
        else:
            print(f'\nStopping server {server_name}...')
            conn.compute.stop_server(server)

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    for server_name in SERVER_NAMES:
        utilities.destroy_server(server_name)
    
    utilities.destroy_router(ROUTER_NAME, SUBNET_NAME)
    utilities.destroy_subnet(SUBNET_NAME)
    utilities.destroy_network(NETWORK_NAME)

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    for server_name in SERVERS:
        server = conn.compute.get_server(conn.compute.find_server(server_name).id)
        if(server == None):
            print(f'\nServer {server_name} does not exist. To create it, run this script with the create option.')
        else:
            print(f'\nGettings status of server {server_name}...')
            print(server.status)


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

