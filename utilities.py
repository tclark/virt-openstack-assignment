import openstack

KEYPAIR = 'sysadminapp'
conn = openstack.connect(could_name='openstack')

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
SECURITY_GROUP = 'default'

SUBNET_IP_VERSION = 4
SUBNET_CIDR = '192.168.50.0/24'


def create_network(network_name):
    network = conn.network.find_network(network_name)
    if(network == None):
        print(f'\nCreating network {network_name}...')
        network = conn.network.create_network(name=network_name)
    else:
        print(f'\nNetwork {network_name} already exists - skipping')


def create_subnet(subnet_name, network_name):
    network = conn.network.find_network(network_name)
    if(network_name == None):
        print(f'\nCOULD NOT FIND NETWORK {network_name}')

    subnet = conn.network.find_subnet(subnet_name)
    if(subnet == None):
        # Move all of these prints to first line.
        print(f'\nCreating subnet {subnet_name}...')
        subnet = conn.network.create_subnet(
            name=subnet_name, network_id=network.id, ip_version=SUBNET_IP_VERSION, cidr=SUBNET_CIDR)
    else:
        print(f'\nSubnet {subnet_name} already exists - skipping')


def create_router(router_name, subnet_name, network_name):
    subnet = conn.network.find_subnet(subnet_name)
    if (subnet == None):
        print(f'\nCOULD NOT FIND SUBNET {subnet_name}')

    network = conn.network.find_network(network_name)
    if (network == None):
        print(f'\nCOULD NOT FIND NETWORK {network_name}')

    router = conn.network.find_router(router_name)
    if (router == None):
        print(f'\nCreating router {router_name}...')
        router = conn.network.create_router(name=router_name, external_gateway_info={
                                            'network_id': network.id})
        router = conn.network.add_interface_to_router(router, subnet.id)
    else:
        print(f'\nRouter {router_name} already exists - skipping')


def create_server(server_name, network_name):
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

    network = conn.network.find_network(network_name)
    if (network == None):
        print(f'\nCOULD NOT FIND NETWORK {network_name}')

    server = conn.compute.find_server(server_name)
    if(server == None):
        print(f'\nCreating server {server_name}...')
        server = conn.compute.create_server(
            name=server_name, image_id=image.id,
            # Should all have IP addresses?
            flavor_id=flavour.id, networks=[{'uuid': network.id}],
            key_name=keypair.name, security_groups=[
                {'sgid': security_group.id}]
        )
    else:
        print(f'\nServer {server_name} already exists - skipping')


def destroy_server(server_name):
    server = conn.compute.find_server(server_name)
    if(server != None):
        print(f'\nDeleting server {server_name}...')
        conn.compute.delete_server(server)
    else:
        print(f'\nServer {server_name} does not exist - skipping')


def destroy_router(router_name, subnet_name):
    subnet = conn.network.find_subnet(subnet_name)
    router = conn.network.find_router(router_name)
    if (router != None):
        print(f'\nDeleting router {router_name}...')
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(router)
    else:
        print(f'\nRouter {router_name} does not exist - skipping')


def destroy_subnet(subnet_name):
    subnet = conn.network.find_subnet(subnet_name)
    if(subnet != None):
        print(f'\nDeleting subnet {subnet_name}...')
        conn.network.delete_subnet(subnet)
    else:
        print(f'\nSubnet {subnet_name} does not exist - skipping')


def destroy_network(network_name):
    network = conn.network.find_network(network_name)
    if(network != None):
        print(f'\nDeleting network {network_name}...')
        conn.network.delete_network(network)
    else:
        print(f'\nNetwork {network_name} does not exist - skipping')


def find_public_network(public_network_name):
    public_net = conn.network.find_network(public_network_name)
    if(public_net == None):
        print(f'\nCOULD NOT FIND NETWORK {public_network_name}')
    return public_net


def add_floating_ip_to_server(server_name, network_name):
    network = conn.network.find_network(network_name)
    if (network == None):
        print(f'\nCOULD NOT FIND NETWORK {network_name}')

    server = conn.compute.find_server(server_name)
    if(server == None):
        print(f'\nCOULD NOT FIND SERVER {server_name}')
    conn.compute.wait_for_server(server)
    if(len(conn.compute.get_server(server.id)['addresses']['chril2-net']) < 2):
        floating_ip = conn.network.create_ip(floating_network_id=network.id)
        conn.compute.add_floating_ip_to_server(
            server, floating_ip.floating_ip_address)
        print(f'Added address {floating_ip["floating_ip_address"]}')
    else:
        print(f'{server_name} already has a floating IP address')


def start_server(server_name):
    server = conn.compute.find_server(server_name)
    if(server == None):
        print(
            f'\nServer {server_name} does not exist. To create it, run this script with the create option.')
    else:
        if(server.status != 'ACTIVE'):
            print(f'\nStarting server {server_name}...')
            conn.compute.start_server(server)
        else:
            print(
                f'\nServer {server_name} has already been started - skipping')


def stop_server(server_name):
    server = conn.compute.find_server(server_name)
    if(server == None):
        print(
            f'\nServer {server_name} does not exist. To create it, run this script with the create option.')
    else:
        if(server.status != 'SHUTOFF'):
            print(f'\nStopping server {server_name}...')
            conn.compute.stop_server(server)
        else:
            print(
                f'\nServer {server_name} has already been stopped - skipping')


def get_server_status(server_name):
    server = conn.compute.get_server(conn.compute.find_server(server_name).id)
    if(server == None):
        print(
            f'\nServer {server_name} does not exist. To create it, run this script with the create option.')
    else:
        print(f'\nGetting status of server {server_name}...')
        print(server.status, conn.compute.get_server(
            server.id)['addresses']['chril2-net'])
