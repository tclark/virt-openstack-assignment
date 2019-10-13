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
    if network is None:
        print(f"\nCreating network {network_name}...")
        network = connection.network.create_network(name=network_name)
    else:
        print(f"\nNetwork {network_name} already exists - skipping")


def create_subnet(subnet_name, network_name):
    """Creates a subnet withing the given network"""
    network = connection.network.find_network(network_name)
    subnet = connection.network.find_subnet(subnet_name)

    if subnet is None:
        # Move all of these prints to first line.
        print(f"\nCreating subnet {subnet_name}...")
        try:
            subnet = connection.network.create_subnet(
                name=subnet_name,
                network_id=network.id,
                ip_version=SUBNET_IP_VERSION,
                cidr=SUBNET_CIDR,
            )
        except:
            print(f"CREATING SUBNET {subnet_name} FAILED")
            if network_name is None:
                print(f"\tCOULD NOT FIND NETWORK {network_name}")
    else:
        print(f"\nSubnet {subnet_name} already exists - skipping")


def create_router(router_name, subnet_name, network_name):
    """Creates a router and adds it to a given network and adds an interface to
    the router for a given subnet"""
    subnet = connection.network.find_subnet(subnet_name)
    network = connection.network.find_network(network_name)
    router = connection.network.find_router(router_name)

    if router is None:
        print(f"\nCreating router {router_name}...")
        try:
            router = connection.network.create_router(
                name=router_name, external_gateway_info={"network_id": network.id}
            )
            router = connection.network.add_interface_to_router(router, subnet.id)
        except:
            print(f"CREATING ROUTER {router_name} FAILED")
            if network is None:
                print(f"\tCOULD NOT FIND NETWORK {network_name}")
            if subnet is None:
                print(f"\tCOULD NOT FIND SUBNET {subnet_name}")
    else:
        print(f"\nRouter {router_name} already exists - skipping")


def create_server(server_name, network_name):
    """Creates a server and adds it to a given network"""
    image = connection.compute.find_image(IMAGE)
    flavour = connection.compute.find_flavor(FLAVOUR)
    keypair = connection.compute.find_keypair(KEYPAIR)
    security_group = connection.network.find_security_group(SECURITY_GROUP)
    network = connection.network.find_network(network_name)
    server = connection.compute.find_server(server_name)

    if server is None:
        print(f"\nCreating server {server_name}...")
        try:
            server = connection.compute.create_server(
                name=server_name,
                image_id=image.id,
                # Should all have IP addresses?
                flavor_id=flavour.id,
                networks=[{"uuid": network.id}],
                key_name=keypair.name,
                security_groups=[{"sgid": security_group.id}],
            )
        except:
            print(f"CREATING SERVER {server_name} FAILED")
            if security_group is None:
                print(f"\tCOULD NOT FIND SECURITY GROUP {SECURITY_GROUP}")
            if network is None:
                print(f"\tCOULD NOT FIND NETWORK {network_name}")
            if keypair is None:
                print(f"\tCOULD NOT FIND KEYPAIR {KEYPAIR}")
            if flavour is None:
                print(f"\tCOULD NOT FIND FLAVOUR {FLAVOUR}")
            if image is None:
                print(f"\tCOULD NOT FIND IMAGE {IMAGE}")
    else:
        print(f"\nServer {server_name} already exists - skipping")


def extract_floating_ips(server):
    """Return a list of floating IPs of a Server as strings."""
    ips = []
    if server.addresses is not None:
        for net in server.addresses:
            for a in server.addresses[net]:
                addrs = []
                if a["OS-EXT-IPS:type"] is "floating":
                    addrs.append(a["addr"])
            ips.extend(addrs)
    return ips


def extract_all_ips(server):
    """Return a list of IPs of a Server as strings."""
    ips = []
    if server.addresses is not None:
        for net in server.addresses:
            for a in server.addresses[net]:
                ips.append(a["addr"])
    return ips


def add_floating_ip_to_server(server_name, network_name):
    """Adds a floating ip to the given server from the given network"""
    print(f"\nAdding floating address to {server_name}...")

    network = connection.network.find_network(network_name)
    server = connection.compute.find_server(server_name)
    try:
        if not extract_floating_ips(server):
            floating_ip = connection.network.create_ip(floating_network_id=network.id)
            connection.compute.add_floating_ip_to_server(
                server, floating_ip.floating_ip_address
            )
            print(f'\tAdded address {floating_ip["floating_ip_address"]}')
        else:
            print(f"\t{server_name} already has a floating IP address")
    except error as e:
        print(e)
        print(f"ADDING FLOATING IP TO {server_name} FAILED")
        if server is None:
            print(f"\tCOULD NOT FIND SERVER {server_name}")
        if network is None:
            print(f"\tCOULD NOT FIND NETWORK {network_name}")


def destroy_server(server_name):
    """Destroys the given server"""
    server = connection.compute.find_server(server_name)
    if server is not None:
        print(f"\nDeleting server {server_name}...")
        ips = extract_floating_ips(server)
        for ip in ips:
            address = connection.network.find_ip(ip)
            print(f"\tReleasing floating IP {ip}...")
            connection.network.delete_ip(address)
            while True:
                if connection.network.find_ip(ip) is None:
                    break
        connection.compute.delete_server(server, ignore_missing=True)
        # Wait until server was deleted
        while True:
            if connection.compute.find_server(server) is None:
                break
    else:
        print(f"\nServer {server_name} does not exist - skipping")


def destroy_router(router_name, subnet_name):
    """Destroys the given router"""
    subnet = connection.network.find_subnet(subnet_name)
    router = connection.network.find_router(router_name)
    if router is not None:
        print(f"\nDeleting router {router_name}...")
        try:
            print(f"\tDeleting interface for {subnet_name}...")
            connection.network.remove_interface_from_router(router, subnet.id)
            print(f"\tFinishing up deleting router {router_name}...")
            connection.network.delete_router(router, ignore_missing=True)
        except:
            print("DELETING ROUTER {router_name} FAILED")
            if subnet is None:
                print(f"\tCOULD NOT FIND SUBNET {subnet_name}")
    else:
        print(f"\nRouter {router_name} does not exist - skipping")


def destroy_subnet(subnet_name):
    """Destroys a given subnet if no interfaces are connected to it"""
    subnet = connection.network.find_subnet(subnet_name)
    if subnet is not None:
        print(f"\nDeleting subnet {subnet_name}...")
        try:
            connection.network.delete_subnet(subnet, ignore_missing=True)
        except:
            print("DELETING SUBNET {subnet_name} FAILED")
            print(
                f"This may be due to servers with ips in its range still building if they were just deleted you may want to run the destroy command again"
            )

    else:
        print(f"\nSubnet {subnet_name} does not exist - skipping")


def destroy_network(network_name):
    """Destroys a given network"""
    network = connection.network.find_network(network_name)
    if network is not None:
        print(f"\nDeleting network {network_name}...")
        for subnet in network.subnet_ids:
            print(f"\tDeleting subnet {subnet.name}...")
            connection.network.delete(subnet)
        try:
            connection.network.delete_network(network, ignore_missing=True)
        except:
            print("DELETING NETWORK {network_name} FAILED")
            print(
                f"This may be due to servers with ips in its range still building if they were just deleted you may want to run the destroy command again"
            )
    else:
        print(f"\nNetwork {network_name} does not exist - skipping")


def start_server(server_name):
    server = connection.compute.find_server(server_name)
    if server is not None:
        server = connection.compute.get_server(server.id)
        if server.status is not "ACTIVE":
            print(f"\nStarting server {server_name}...")
            connection.compute.start_server(server)
        else:
            print(f"\nServer {server_name} is already running - skipping")
    else:
        print(
            (
                f"\nServer {server_name} does not exist. To create it,"
                " run this script with the create option."
            )
        )


def stop_server(server_name):
    server = connection.compute.find_server(server_name)
    if server is None:
        print(
            (
                f"\nServer {server_name} does not exist. To create it,"
                " run this script with the create option."
            )
        )
    else:
        server = connection.compute.get_server(server.id)
        if server.status is not "SHUTOFF":
            print(f"\nStopping server {server_name}...")
            connection.compute.stop_server(server)
            connection.compute.wait_for_server(server, status="SHUTOFF")
        else:
            print(f"\nServer {server_name} has already been stopped - skipping")


def get_server_status(server_name):
    server = connection.compute.find_server(server_name)
    if server is None:
        print(
            (
                f"\nServer {server_name} does not exist. To create it,"
                " run this script with the create option."
            )
        )
    else:
        server = connection.compute.get_server(server.id)
        print(f"\nGetting status of server {server_name}...")
        print("Status:", server.status)
        print("IP addresses:", extract_all_ips(server))

