import openstack
from connection import connection.py

KEYPAIR = 'sysadminapp'

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
SECURITY_GROUP = 'assignment2'

SUBNET_IP_VERSION = 4
SUBNET_CIDR = '192.168.50.0/24'


def create_network(network_name):
    network = conn.network.find_network(network_name)
    if(network is None):
        print(f'\nCreating network {network_name}...')
        network = connection.network.create_network(name=network_name)
    else:
        print(f'\nNetwork {network_name} already exists - skipping')


def create_subnet(subnet_name, network_name):
    network = connection.network.find_network(network_name)
    if(network_name is None):
        print(f'\nCOULD NOT FIND NETWORK {network_name}')

    subnet = connection.network.find_subnet(subnet_name)
    if(subnet is None):
        # Move all of these prints to first line.
        print(f'\nCreating subnet {subnet_name}...')
        subnet = connection.network.create_subnet(
            name=subnet_name, network_id=network.id, ip_version=SUBNET_IP_VERSION, cidr=SUBNET_CIDR)
    else:
        print(f'\nSubnet {subnet_name} already exists - skipping')


def create_router(router_name, subnet_name, network_name):
    subnet = connection.network.find_subnet(subnet_name)
    if (subnet is None):
        print(f'\nCOULD NOT FIND SUBNET {subnet_name}')

    network = connection.network.find_network(network_name)
    if (network is None):
        print(f'\nCOULD NOT FIND NETWORK {network_name}')

    router = connection.network.find_router(router_name)
    if (router is None):
        print(f'\nCreating router {router_name}...')
        router = connection.network.create_router(name=router_name, external_gateway_info={
            'network_id': network.id})
        router = connection.network.add_interface_to_router(router, subnet.id)
    else:
        print(f'\nRouter {router_name} already exists - skipping')


def create_server(server_name, network_name):
    image = connection.compute.find_image(IMAGE)
    if(image is None):
        print(f'\nCOULD NOT FIND IMAGE {IMAGE}')

    flavour = connection.compute.find_flavor(FLAVOUR)
    if(flavour is None):
        print(f'\nCOULD NOT FIND FLAVOUR {FLAVOUR}')

    keypair = connection.compute.find_keypair(KEYPAIR)
    if(keypair is None):
        print(f'\nCOULD NOT FIND KEYPAIR {KEYPAIR}')

    security_group = connection.network.find_security_group(SECURITY_GROUP)
    if(security_group is None):
        print(f'\nCOULD NOT FIND SECURITY GROUP {SECURITY_GROUP}')

    network = connection.network.find_network(network_name)
    if (network is None):
        print(f'\nCOULD NOT FIND NETWORK {network_name}')

    server = connection.compute.find_server(server_name)
    if(server is None):
        print(f'\nCreating server {server_name}...')
        server = connection.compute.create_server(
            name=server_name, image_id=image.id,
            # Should all have IP addresses?
            flavor_id=flavour.id, networks=[{'uuid': network.id}],
            key_name=keypair.name, security_groups=[
                {'sgid': security_group.id}]
        )
    else:
        print(f'\nServer {server_name} already exists - skipping')

def add_floating_ip_to_server(server_name, network_name):
    network = conn.network.find_network(network_name)
    if (network is None):
        print(f'\nCOULD NOT FIND NETWORK {network_name}')

    server = conn.compute.find_server(server_name)
    if(server is None):
        print(f'\nCOULD NOT FIND SERVER {server_name}')

    conn.compute.wait_for_server(server)
    if(len(conn.compute.get_server(server.id)['addresses'][network_name]) < 2):
        floating_ip = conn.network.create_ip(floating_network_id=network.id)
        conn.compute.add_floating_ip_to_server(
            server, floating_ip.floating_ip_address)
        print(f'Added address {floating_ip["floating_ip_address"]}')
    else:
        print(f'{server_name} already has a floating IP address')
