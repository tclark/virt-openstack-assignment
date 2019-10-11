import argparse
import openstack

conn = openstack.connect(cloud_name='openstack')

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'woodjj1-net'
KEYPAIR = 'woodjj1-key'
SECURITY = 'assignment2'
SUBNET = '192.168.50.0/24'
SERVERLIST = { 'woodjj1-web', 'woodjj1-app', 'woodjj1-db' }

public_net = conn.network.find_network('public-net')

def create():
    ''' Create a set of Openstack resources '''
    
    #Create Network
    print("Creating Network......")

    # Finding network, subnet and router
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet('woodjj1-subnet')
    router = conn.network.find_router('woodjj1-rtr')

    # Create network when its name can not be found on catalyst cloud
    if network:
        print("Network resource already exist")
    else:
        network = conn.network.create_network(
            name=NETWORK
        )
        print("Network resource created")

    # Create subnet when its name can not be found on catalyst cloud
    if subnet:
        print("Subnet already exists")
    else:
        subnet = conn.network.create_subnet(
            name='woodjj1-subnet',
            network_id=network.id,
            ip_version='4',
            cidr=SUBNET
        )
        print("Subnet created")

