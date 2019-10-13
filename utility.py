import openstack

conn = openstack.connect(could_name='openstack')


def create_network(network_name):
    print(f'\nCreating network {network_name}...')

    network = conn.network.find_network(network_name)
    if network is None:
        network = conn.network.create_network(name=network_name)
        print('\tNetwork created')
    else:
        print('\tNetwork already exists - skipping')


def create_subnet(subnet_name, network_name, subnet_ip_version, subnet_cidr):
    print(f'\nCreating subnet {subnet_name}...')

    network = conn.network.find_network(network_name)
    if network is None:
        print(f'\tCOULD NOT FIND NETWORK {network_name}')

    subnet = conn.network.find_subnet(subnet_name)
    if subnet is None:
        subnet = conn.network.create_subnet(
            name=subnet_name,
            network_id=network.id,
            ip_version=subnet_ip_version,
            cidr=subnet_cidr)
        print('\tSubnet created')
    else:
        print('\tSubnet already exists - skipping')


def create_router(router_name, network_name):
    print(f'\nCreating router {router_name}...')

    network = conn.network.find_network(network_name)
    if network is None:
        print(f'\tCOULD NOT FIND NETWORK {network_name}')

    router = conn.network.find_router(router_name)
    if router is None:
        router = conn.network.create_router(
            name=router_name,
            external_gateway_info={
                'network_id': network.id
            })
        print('\tRouter created')
    else:
        print('\tRouter already exists - skipping')


def create_server(
        server_name, image_name, flavour_name,
        keypair_name, security_group_name, network_name):
    print(f'\nCreating server {server_name}...')

    image = conn.compute.find_image(image_name)
    if image is None:
        print(f'\tCOULD NOT FIND IMAGE {image_name}')

    flavour = conn.compute.find_flavor(flavour_name)
    if flavour is None:
        print(f'\tCOULD NOT FIND FLAVOUR {flavour_name}')

    keypair = conn.compute.find_keypair(keypair_name)
    if keypair is None:
        print(f'\tCOULD NOT FIND KEYPAIR {keypair_name}')

    security_group = conn.network.find_security_group(security_group_name)
    if security_group is None:
        print(f'\tCOULD NOT FIND SECURITY GROUP {security_group_name}')

    network = conn.network.find_network(network_name)
    if network is None:
        print(f'\tCOULD NOT FIND NETWORK {network_name}')

    server = conn.compute.find_server(server_name)
    if server is None:
        server = conn.compute.create_server(
            name=server_name, image_id=image.id,
            flavor_id=flavour.id, networks=[{'uuid': network.id}],
            key_name=keypair.name, security_groups=[
                {'sgid': security_group.id}]
        )
        print('\tWaiting for server to start')
        conn.compute.wait_for_server(server)
        print('\tCreated server')
    else:
        print('\tServer already exists - skipping')


def destroy_server(server_name):
    print(f'\nDeleting server {server_name}...')

    server = conn.compute.find_server(server_name)
    if server is not None:
        conn.compute.delete_server(server)
        print('\tDeleted server')
    else:
        print('\tServer does not exist - skipping')


def destroy_router(router_name, subnet_name):
    print(f'\nDeleting router {router_name}...')

    subnet = conn.network.find_subnet(subnet_name)
    router = conn.network.find_router(router_name)
    if router is not None:
        router_no_interface = conn.network.remove_interface_from_router(
            router, subnet.id)
        conn.network.delete_router(router_no_interface)
        print('\tDeleted router')
    else:
        print('\tRouter does not exist - skipping')


def destroy_subnet(subnet_name):
    print(f'\nDeleting subnet {subnet_name}...')

    subnet = conn.network.find_subnet(subnet_name)
    if subnet is not None:
        conn.network.delete_subnet(subnet)
        print('\tDeleted subnet')
    else:
        print(f'\nSubnet {subnet_name} does not exist - skipping')


def destroy_network(network_name):
    print(f'\nDeleting network {network_name}...')

    network = conn.network.find_network(network_name)
    if network is not None:
        conn.network.delete_network(network)
        print('\tDeleted network')
    else:
        print('\tNetwork does not exist - skipping')


def add_interface_to_router(router_name, subnet_name):
    print((
        f'\nAdding interface for {subnet_name}'
        f' to {router_name}'))

    subnet = conn.network.find_subnet(subnet_name)
    if subnet is None:
        print(f'\nCOULD NOT FIND SUBNET {subnet_name}')

    router = conn.network.find_router(router_name)
    if router is not None:
        router = conn.network.add_interface_to_router(router, subnet.id)
        print('\tInterface added')
    else:
        print('\tCOULD NOT FIND ROUTER')


def add_floating_ip_to_server(server_name, network_name):
    network = conn.network.find_network(network_name)
    if network is None:
        print(f'\nCOULD NOT FIND NETWORK {network_name}')

    server = conn.compute.find_server(server_name)
    if server is None:
        print(f'\nCOULD NOT FIND SERVER {server_name}')

    print(f'\nAdding floating address to {server_name}...')
    server = conn.compute.get_server(server.id)
    if server.status == 'ACTIVE':
        server_addresses = server['addresses']['chril2-net']
        if len(server_addresses) < 2:
            floating_ip = conn.network.create_ip(floating_network_id=network.id)
            conn.compute.add_floating_ip_to_server(
                server, floating_ip.floating_ip_address)
            print(f'\tAssigned address {floating_ip["floating_ip_address"]}')
        else:
            print('\tThe server already has a floating IP address - skipping')
    else:
        print('\tThe server must be active to add a floating IP address')


def start_server(server_name):
    server = conn.compute.find_server(server_name)
    if server is None:
        print((
            f'\nServer {server_name} does not exist. To create it,'
            ' run this script with the create option.'))
    else:
        server = conn.compute.get_server(server.id)
        if(server.status != 'ACTIVE'):
            print(f'\nStarting server {server_name}...')
            conn.compute.start_server(server)
        else:
            print(
                f'\nServer {server_name} is already running - skipping')


def stop_server(server_name):
    server = conn.compute.find_server(server_name)
    if server is None:
        print((
            f'\nServer {server_name} does not exist. To create it,'
            ' run this script with the create option.'))
    else:
        server = conn.compute.get_server(server.id)
        if(server.status != 'SHUTOFF'):
            print(f'\nStopping server {server_name}...')
            conn.compute.stop_server(server)
        else:
            print(
                f'\nServer {server_name} has already been stopped - skipping')


def get_server_status(server_name):
    server = conn.compute.find_server(server_name)
    if server is None:
        print((
            f'\nServer {server_name} does not exist. To create it,'
            ' run this script with the create option.'))
    else:
        server = conn.compute.get_server(server.id)
        print(f'\nGetting status of server {server_name}...')
        print(server.status)
        addresses = server['addresses']['chril2-net']
        for address in addresses:
            print(address['addr'])
