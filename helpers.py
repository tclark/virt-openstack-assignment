import openstack
from connection import connection

KEYPAIR = "sysadminapp"

IMAGE = "ubuntu-minimal-16.04-x86_64"
FLAVOUR = "c1.c1r1"
SECURITY_GROUP = "assignment2"

SUBNET_IP_VERSION = 4
SUBNET_CIDR = "192.168.50.0/24"

def create_network(network_name):
    """Creates a network"""
    network = connection.network.find_network(network_name)
    if(network is None):
        print(f"\nCreating network {network_name}...")
        network = connection.network.create_network(name=network_name)
    else:
        print(f"\nNetwork {network_name} already exists - skipping")

def create_subnet(subnet_name, network_name):
    """Creates a subnet withing the given network"""
    network = connection.network.find_network(network_name)
    if(network_name is None):
        print(f"\nCOULD NOT FIND NETWORK {network_name}")

    subnet = connection.network.find_subnet(subnet_name)
    if(subnet is None):
        # Move all of these prints to first line.
        print(f"\nCreating subnet {subnet_name}...")
        subnet = connection.network.create_subnet(
            name=subnet_name, network_id=network.id, ip_version=SUBNET_IP_VERSION, cidr=SUBNET_CIDR)
    else:
        print(f"\nSubnet {subnet_name} already exists - skipping")

#FIXME: this needs broken up
def create_router(router_name, subnet_name, network_name):
    """Creates a router and adds it to a given network and adds an interface to
    the router for a given subnet"""
    subnet = connection.network.find_subnet(subnet_name)
    if (subnet is None):
        print(f"\nCOULD NOT FIND SUBNET {subnet_name}")

    network = connection.network.find_network(network_name)
    if (network is None):
        print(f"\nCOULD NOT FIND NETWORK {network_name}")

    router = connection.network.find_router(router_name)
    if (router is None):
        print(f"\nCreating router {router_name}...")
        router = connection.network.create_router(name=router_name, external_gateway_info={
            "network_id": network.id})
        router = connection.network.add_interface_to_router(router, subnet.id)
    else:
        print(f"\nRouter {router_name} already exists - skipping")

def create_server(server_name, network_name):
    """Creates a server and adds it to a given network"""
    image = connection.compute.find_image(IMAGE)
    if(image is None):
        print(f"\nCOULD NOT FIND IMAGE {IMAGE}")

    flavour = connection.compute.find_flavor(FLAVOUR)
    if(flavour is None):
        print(f"\nCOULD NOT FIND FLAVOUR {FLAVOUR}")

    keypair = connection.compute.find_keypair(KEYPAIR)
    if(keypair is None):
        print(f"\nCOULD NOT FIND KEYPAIR {KEYPAIR}")

    security_group = connection.network.find_security_group(SECURITY_GROUP)
    if(security_group is None):
        print(f"\nCOULD NOT FIND SECURITY GROUP {SECURITY_GROUP}")

    network = connection.network.find_network(network_name)
    if (network is None):
        print(f"\nCOULD NOT FIND NETWORK {network_name}")

    server = connection.compute.find_server(server_name)
    if(server is None):
        print(f"\nCreating server {server_name}...")
        server = connection.compute.create_server(
            name=server_name, image_id=image.id,
            # Should all have IP addresses?
            flavor_id=flavour.id, networks=[{"uuid": network.id}],
            key_name=keypair.name, security_groups=[
                {"sgid": security_group.id}]
        )
    else:
        print(f"\nServer {server_name} already exists - skipping")

def extract_floating_ips(server):
    """Return a list of floating IPs of a Server as strings."""
    ips = []
    for net in server.addresses:
        for a in server.addresses[net]:
            addrs = []
            if a["OS-EXT-IPS:type"] == "floating":
                addrs.append(a["addr"])
        ips.extend(addrs)
    return ips

def extract_all_ips(server):
    """Return a list of IPs of a Server as strings."""
    ips = []
    for net in server.addresses:
        for a in server.addresses[net]:
            ips.append(a['addr'])
    return ips

def add_floating_ip_to_server(server_name, network_name):
    """Adds a floating ip to the given server from the given network"""
    network = connection.network.find_network(network_name)
    if (network is None):
        print(f"\nCOULD NOT FIND NETWORK {network_name}")

    server = connection.compute.find_server(server_name)
    if(server is None):
        print(f"\nCOULD NOT FIND SERVER {server_name}")

    connection.compute.wait_for_server(server)
    if not extract_floating_ips(server):
        floating_ip = connection.network.create_ip(
            floating_network_id=network.id)
        connection.compute.add_floating_ip_to_server(
            server, floating_ip.floating_ip_address)
        print(f'Added address {floating_ip["floating_ip_address"]}')
    else:
        print(f"{server_name} already has a floating IP address")

def destroy_server(server_name):
    """Destroys the given server"""
    server = connection.compute.find_server(server_name)
    if(server != None):
        print(f"\nDeleting server {server_name}...")
        connection.compute.delete_server(server)
    else:
        print(f"\nServer {server_name} does not exist - skipping")

def destroy_router(router_name, subnet_name):
    """Destroys the given router"""
    subnet = connection.network.find_subnet(subnet_name)
    router = connection.network.find_router(router_name)
    if (router != None):
        print(f"\nDeleting router {router_name}...")
        # FIXME: Does this have to be here
        connection.network.remove_interface_from_router(router, subnet.id)
        connection.network.delete_router(router)
    else:
        print(f"\nRouter {router_name} does not exist - skipping")

def destroy_subnet(subnet_name):
    """Destroys a given subnet if no interfaces are connected to it"""
    subnet = connection.network.find_subnet(subnet_name)
    if(subnet != None):
        print(f"\nDeleting subnet {subnet_name}...")
        connection.network.delete_subnet(subnet)
    else:
        print(f"\nSubnet {subnet_name} does not exist - skipping")

def destroy_network(network_name):
    """Destroys a given network"""
    network = connection.network.find_network(network_name)
    if(network != None):
        print(f"\nDeleting network {network_name}...")
        connection.network.delete_network(network)
    else:
        print(f"\nNetwork {network_name} does not exist - skipping")

def start_server(server_name):
    server = connection.compute.find_server(server_name)
    if server is not None:
        server = connection.compute.get_server(server.id)
        if(server.status != 'ACTIVE'):
            print(f'\nStarting server {server_name}...')
            connection.compute.start_server(server)
        else:
            print(
                f'\nServer {server_name} is already running - skipping')
    else:
        print((
            f'\nServer {server_name} does not exist. To create it,'
            ' run this script with the create option.'))

def stop_server(server_name):
    server = connection.compute.find_server(server_name)
    if server is None:
        print((
            f'\nServer {server_name} does not exist. To create it,'
            ' run this script with the create option.'))
    else:
        server = connection.compute.get_server(server.id)
        if(server.status != 'SHUTOFF'):
            print(f'\nStopping server {server_name}...')
            connection.compute.stop_server(server)
        else:
            print(
                f'\nServer {server_name} has already been stopped - skipping')

def get_server_status(server_name):
    server = connection.compute.find_server(server_name)
    if server is None:
        print((
            f'\nServer {server_name} does not exist. To create it,'
            ' run this script with the create option.'))
    else:
        server = connection.compute.get_server(server.id)
        print(f'\nGetting status of server {server_name}...')
        print('Status:', server.status)
        print('IP addresses:', extract_all_ips(server))

