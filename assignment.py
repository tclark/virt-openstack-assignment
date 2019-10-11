#!/usr/bin/env python
import argparse
import openstack


os_connect = openstack.connect(cloud_name='openstack')
# Constants that will be used throughout the script
# Kept here to be changed easily at the users whim
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOR = 'c1.c1r1'
KEYPAIR = 'mckeja4-key'
SUBNET = 'mckeja4-subnet'
NETWORK = 'mckeja4-net'
ROUTER = 'mckeja4-router'
SECURITY_GROUP = 'assignment2'
PUBNET_NAME = 'public-net'
SERVER_NAMES = ['mckeja4-web', 'mckeja4-app', 'mckeja4-db']

def create():
    #I have prefaced the Openstack ???Objects/Structs??? with OS
    os_image = os_connect.compute.find_image(IMAGE)
    os_flavor = os_connect.compute.find_flavor(FLAVOR)
    os_keypair = os_connect.compute.find_keypair(KEYPAIR)
    os_public_net = os_connect.network.find_network(PUBNET_NAME)
    os_security_group = os_connect.network.find_security_group(SECURITY_GROUP)
    os_network = os_connect.network.find_network(NETWORK)
    
    
    if os_network:
        print(NETWORK, 'already exists! Skipping...')
        
    else:
        print('Creating', NETWORK)
        os_network = os_connect.network.create_network(name=NETWORK)

    os_subnet = os_connect.network.find_subnet(SUBNET)
    if os_subnet:
        print(SUBNET, 'already exists')
    else:
        print('Creating', SUBNET)
        os_subnet = os_connect.network.create_subnet(name=SUBNET,
                                            cidr='192.168.50.0/24',
                                            ip_version=4,
                                            network_id=os_network.id)

    os_router = os_connect.network.find_router(ROUTER)
    if os_router:
        print(ROUTER, 'already exists')
    else:
        print('Creating', ROUTER)
        ext = {'network_id': os_public_net.id}
        os_router = os_connect.network.create_router(name=ROUTER,
                                            external_gateway_info=ext)
        print('Creating interface for', SUBNET)
        os_connect.network.add_interface_to_router(os_router, os_subnet.id)

    for server in SERVER_NAMES:
        s = os_connect.compute.find_server(server)
        if s:
            print(server, 'already exists')
        else:
            print('Creating', server)
            s = os_connect.compute.create_server(name=server,
                                           image_id=os_image.id,
                                           flavor_id=os_flavor.id,
                                           key_name=os_keypair.name,
                                           networks=[{'uuid': os_network.id}],
                                           security_groups=[os_security_group])

    web = os_connect.compute.find_server('mckeja4-web')
    web = os_connect.compute.get_server(web.id)
    os_connect.compute.wait_for_server(web)
 
    #Creates a list of avalible Floating IPS
    floatingips = []
    for net in web.addresses:
        for a in web.addresses[net]:
            addrs = []
            if a['OS-EXT-IPS:type'] == 'floating':
                addrs.append(a['addr'])
        floatingips.extend(addrs)
    #Closes the program if none are avaliable
    if floatingips.__len__ == 0:
        print("There are no floating ips avalible")
        exit

    print('Creating floating IP address for mckeja4-web... ', end='')
    web_ip = os_connect.network.create_ip(floating_network_id=os_public_net.id)
    print('Got IP:', web_ip.floating_ip_address)

    print('Assigning address to mckeja4-web')
    os_connect.compute.add_floating_ip_to_server(web,
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
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    pass

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
