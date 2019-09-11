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
        ips.extend([a['addr'] for a in server.addresses[net]
                    if a['OS-EXT-IPS:type'] == 'floating'])
    return ips


def create():
    ''' Create a set of Openstack resources '''
    image = conn.compute.find_image(IMAGE)
    flavor = conn.compute.find_flavor(FLAVOR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    public_net = conn.network.find_network(PUBNET_NAME)
    security_group = conn.network.find_security_group(SECURITY_GROUP)

    # TODO: check if resources already exist before creation

    print('Creating', NETWORK)
    network = conn.network.create_network(name=NETWORK)
    print('Creating', SUBNET)
    subnet = conn.network.create_subnet(name=SUBNET, network_id=network.id,
        cidr='192.168.50.0/24', ip_version=4)

    print('Creating', ROUTER)
    router = conn.network.create_router(name=ROUTER,
        external_gateway_info={'network_id': public_net.id})

    print('Creating interface for', SUBNET)
    conn.network.add_interface_to_router(router, subnet.id)

    for name in SERVER_NAMES:
        print('Creating', name)
        s = conn.compute.create_server(name=name, image_id=image.id,
                flavor_id=flavor.id, key_name=keypair.name,
                networks=[{'uuid': network.id}],
                security_groups=[security_group])

        if name == 'hallmg1-web':
            print('Creating floating IP address for hallmg1-web... ', end='')
            web_ip = conn.network.create_ip(floating_network_id=public_net.id)
            print('Got IP:', web_ip.floating_ip_address)

            print('Assigning address to', name)
            conn.compute.wait_for_server(s)
            conn.compute.add_floating_ip_to_server(s,
                web_ip.floating_ip_address)


def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    pass


def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    pass


def destroy():
    """Tear down the Openstack resources produced by the create action."""

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
    ''' Print a status report on the OpenStack
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
        'create'  : create,
        'run'     : run,
        'stop'    : stop,
        'destroy' : destroy,
        'status'  : status
        }

    action = operations.get(operation, lambda: print('{}: no such operation'.format(operation)))
    action()
