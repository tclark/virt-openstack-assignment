#!/usr/bin/env python
import argparse
import openstack


IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOR = 'c1.c1r1'
KEYPAIR = 'hallmg1-key'
SUBNET = 'hallmg1-subnet'
NETWORK = 'hallmg1-net'
ROUTER = 'hallmg1-router'
SECURITY_GROUP = 'assignment2'
PUBNET_NAME = 'public-net'
SERVER_NAMES = ['hallmg1-web', 'hallmg1-app', 'hallmg1-db']

conn = openstack.connect(cloud_name='openstack')


def extract_ips(server):
    """Return a list of floating IPs of a Server as strings."""
    ips = []
    for net in server.addresses:
        for a in server.addresses[net]:
            addrs = []
            if a['OS-EXT-IPS:type'] == 'floating':
                addrs.append(a['addr'])
        ips.extend(addrs)
    return ips


def create():
    """Create a set of Openstack resources."""
    image = conn.compute.find_image(IMAGE)
    flavor = conn.compute.find_flavor(FLAVOR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    public_net = conn.network.find_network(PUBNET_NAME)
    security_group = conn.network.find_security_group(SECURITY_GROUP)

    network = conn.network.find_network(NETWORK)
    if network:
        print(NETWORK, 'already exists')
    else:
        print('Creating', NETWORK)
        network = conn.network.create_network(name=NETWORK)

    subnet = conn.network.find_subnet(SUBNET)
    if subnet:
        print(SUBNET, 'already exists')
    else:
        print('Creating', SUBNET)
        subnet = conn.network.create_subnet(name=SUBNET,
                                            cidr='192.168.50.0/24',
                                            ip_version=4,
                                            network_id=network.id)

    router = conn.network.find_router(ROUTER)
    if router:
        print(ROUTER, 'already exists')
    else:
        print('Creating', ROUTER)
        ext = {'network_id': public_net.id}
        router = conn.network.create_router(name=ROUTER,
                                            external_gateway_info=ext)
        print('Creating interface for', SUBNET)
        conn.network.add_interface_to_router(router, subnet.id)

    for name in SERVER_NAMES:
        s = conn.compute.find_server(name)
        if s:
            print(name, 'already exists')
        else:
            print('Creating', name)
            s = conn.compute.create_server(name=name,
                                           image_id=image.id,
                                           flavor_id=flavor.id,
                                           key_name=keypair.name,
                                           networks=[{'uuid': network.id}],
                                           security_groups=[security_group])

    web = conn.compute.find_server('hallmg1-web')
    web = conn.compute.get_server(web.id)
    conn.compute.wait_for_server(web)
    # `extract_ips(web)`evaluates to False
    # if the server does not have any floating IP addresses.
    if extract_ips(web):
        pass
    else:
        print('Creating floating IP address for hallmg1-web... ', end='')
        web_ip = conn.network.create_ip(floating_network_id=public_net.id)
        print('Got IP:', web_ip.floating_ip_address)

        print('Assigning address to hallmg1-web')
        conn.compute.add_floating_ip_to_server(web,
                                               web_ip.floating_ip_address)


def run():
    """Start the virtual machines if they are not already running."""
    for name in SERVER_NAMES:
        s = conn.compute.find_server(name)
        if not s:
            print(name, 'not found, skipping')
        else:
            s = conn.compute.get_server(s)
            print('Sarting {}... '.format(name), end='')
            try:
                conn.compute.start_server(s.id)
            # Openstack will raise a ConflictException here
            # if the server is already active.
            except openstack.exceptions.ConflictException:
                print('Already active')
            else:
                conn.compute.wait_for_server(s)
                print('OK')


def stop():
    """Stop the virtual machines if they are running."""
    for name in SERVER_NAMES:
        s = conn.compute.find_server(name)
        if not s:
            print(name, 'not found, skipping')
        else:
            s = conn.compute.get_server(s.id)
            print('Shutting off {}... '.format(name), end='')
            try:
                conn.compute.stop_server(s.id)
            # Openstack will raise a ConflictExpection here
            # is the server is already shut down.
            except openstack.exceptions.ConflictException:
                print('Already shut down')
            else:
                conn.compute.wait_for_server(s, status='SHUTOFF')
                print('OK')


def destroy():
    """Tear down the Openstack resources made by the create action."""

    # TODO: this could break the deletion of the router and network
    #       if the subnet does not exist
    subnet = conn.network.find_subnet(SUBNET)

    # Delete servers if they exist.
    for name in SERVER_NAMES:
        s = conn.compute.find_server(name)
        if s:
            s = conn.compute.get_server(s)
            ips = extract_ips(s)
            # Release any floating IP addresses.
            for ip in ips:
                addr = conn.network.find_ip(ip)
                print('Releasing floating IP', ip)
                conn.network.delete_ip(addr)
            print('Deleting', name)
            conn.compute.delete_server(s, ignore_missing=True)
            # Waiting for the servers to actually be deleted ensures
            # their ports are also deleted so we can delete the network.
            print('Waiting for {} to be deleted'.format(name))
            while s:
                s = conn.compute.find_server(name)
        else:
            print('Unable to find {}, skipping'.format(name))

    # Delete router if it exists.
    router = conn.network.find_router(ROUTER)
    if router:
        # The subnet interface must be removed before deleting the router.
        print('Deleting interface for', SUBNET)
        conn.network.remove_interface_from_router(router, subnet.id)
        # Now we can delete the router.
        print('Deleting', ROUTER)
        conn.network.delete_router(router, ignore_missing=True)
    else:
        print('Unable to find {}, skipping'.format(ROUTER))

    # Delete network if it exists.
    network = conn.network.find_network(NETWORK)
    if network:
        print('Deleting', SUBNET)
        conn.network.delete_subnet(subnet, ignore_missing=True)
        print('Deleting', NETWORK)
        conn.network.delete_network(network, ignore_missing=True)
    else:
        print('Unable to find {}, skipping'.format(NETWORK))


def status():
    """Print statuses of the virtual machines made by the create action."""
    servers = []
    # Get info for all servers.
    for name in SERVER_NAMES:
        print('Fetching status of {}...'.format(name), end=' ')
        s = conn.compute.find_server(name)
        # Retrieve full server information when possible.
        if s:
            s = conn.compute.get_server(s.id)
            servers.append(s)
            print('OK')
        else:
            print('NOT FOUND')

    # Display status of all servers that were found.
    for server in servers:
        print('\n{}: {}'.format(server.name, server.status))
        ips = extract_ips(server)
        if ips:
            print('Floating IP Addresses:')
            for i in ips:
                print(i)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', help=('One of "create", "run",'
                        ' "stop", "destroy", or "status"'))
    args = parser.parse_args()
    operation = args.operation

    operations = {
        'create': create,
        'run': run,
        'stop': stop,
        'destroy': destroy,
        'status': status}

    action = operations.get(operation, lambda:
                            print('{}: no such operation'.format(operation)))
    action()
