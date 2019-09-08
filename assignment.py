#!/usr/bin/env
import argparse
import openstack

KEYPAIR = 'sysadminapp'
conn = openstack.connect(could_name='openstack')

SUBNET_NAME = 'chril2-subnet'
SUBNET_IP_VERSION = 4
SUBNET_CIDR = '192.168.50.0/24'
NETWORK_NAME = 'chril2-net'
PUBLIC_NETWORK_NAME = 'public-net'

ROUTER_NAME = 'chril2-rtl'
SERVERS = ['chril2-web', 'chril2-app', 'chril2-db']
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
SECURITY_GROUP = 'default'

def create():
    ''' Create a set of Openstack resources '''
    network = conn.network.find_network(NETWORK_NAME)
    if(network == None):
        print(f'\nCreating network {NETWORK_NAME}...')
        network = conn.network.create_network(name=NETWORK_NAME)
    else:
        print(f'\nNetwork {NETWORK_NAME} already exists - skipping')

    subnet = conn.network.find_subnet(SUBNET_NAME)
    if(subnet == None):
        print(f'\nCreating subnet {SUBNET_NAME}...')
        subnet = conn.network.create_subnet(name=SUBNET_NAME, network_id=network.id, ip_version=SUBNET_IP_VERSION, cidr=SUBNET_CIDR)
    else:
        print(f'\nSubnet {SUBNET_NAME} already exists - skipping')

    public_net = conn.network.find_network(PUBLIC_NETWORK_NAME)
    if(public_net == None):
        print(f'\nCOULD NOT FIND NETWORK {PUBLIC_NETWORK_NAME}')

    router = conn.network.find_router(ROUTER_NAME)
    if (router == None):
        print(f'\nCreating router {ROUTER_NAME}...')
        router = conn.network.create_router(name=ROUTER_NAME, external_gateway_info={'network_id': public_net.id})
        router = conn.network.add_interface_to_router(router, subnet.id)
    else:
        print(f'\nRouter {ROUTER_NAME} already exists - skipping')

    image = conn.compute.find_image(IMAGE)
    if(image == None):
        print(f'\nCOULD NOT FIND IMAGE {IMAGE}')

    flavour = conn.compute.find_flavor(FLAVOUR)
    if(flavour == None):
        print(f'\nCOULD NOT FIND FLAVOUR {FLAVOUR}')
    
    keypair = conn.compute.find_keypair(KEYPAIR)
    if(keypair == None):
        print(f'\nCOULD NOT FIND KEYPAIR {KEYPAIR}')
    
    security_group = conn.network.find_security_group(SECURITY_GROUP)
    if(security_group == None):
        print(f'\nCOULD NOT FIND SECURITY GROUP {SECURITY_GROUP}')
    
    for server_name in SERVERS:
        server = conn.compute.find_server(server_name)
        if( server == None):
            print(f'\nCreating server {server_name}...')
            server = conn.compute.create_server(
                    name=server_name, image_id=image.id, 
                    flavor_id=flavour.id, networks=[{'uuid':network.id}], # Should all have IP addresses?
                    key_name=keypair.name, security_groups=[{'sgid':security_group.id}]
            )
        else:
            print(f'\nServer {server_name} already exists - skipping')
        
        # Adding floating IP to web server.
        if(server_name == 'chril2-web'): 
            if(conn.compute.get_server(server.id).addresses == None):
                print('Adding floating IP to chril2_web')
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
                conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)
            else:
                print('Chril2 already has a floating IP address')
    pass

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
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    for server_name in SERVERS:
        server = conn.compute.find_server(server_name)
        if(server == None):
            print(f'\nServer {server_name} does not exist. To create it, run this script with the create option.')
        else:
            print(f'\nStopping server {server_name}...')
            conn.compute.stop_server(server)
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
    for server_name in SERVERS:
        server = conn.compute.get_server(conn.compute.find_server(server_name).id)
        if(server == None):
            print(f'\nServer {server_name} does not exist. To create it, run this script with the create option.')
        else:
            print(f'\nGettings status of server {server_name}...')
            print(server.status)
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

