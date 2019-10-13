#!/usr/bin/env
import argparse
import openstack
import time

conn = openstack.connect(cloud_name='openstack')

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
KEYPAIR = 'zetksm1-key'
NETWORK = 'zetksm1-network'
GROUP = 'assignment2'
SUBNET_NAME = 'zetksm1-subnet'
IP_VERSION='4'
CIDR='192.168.50.0/24'


def create():
    ''' Create a set of Openstack resources '''
    '''Creating the network'''
    network = conn.network.find_network('zetksm1-network')
    if network is None:
        network = conn.network.create_network(name='zetksm1-network')
        print("Network succesfully created")
    else: 
        print("This network already exists")
    
    '''Creating the subnet'''

    subnet = conn.network.find_subnet('zetksm1-subnet')
    if subnet is None:
         subnet = conn.network.create_subnet(
         name=SUBNET_NAME,
         network_id=network.id,
         ip_version=IP_VERSION,
         cidr=CIDR
         )
         print("Subnet has been successfully created")
    else:
         print("Subnet already exists")
   
    '''Creating the Router'''
    public_net = conn.network.find_network('public-net')
    zetksm1_rtr = conn.network.find_router('zetksm1-rtr')

    if zetksm1_rtr is None:
        zetksm1_rtr = conn.network.create_router(name='zetksm1-rtr',
        admin_state_up=True,
        ext_gateway_net_id=public_net.id)
        print("Router successfully created")

    else:
        print("This Router already exists")

    image = conn.compute.find_image(IMAGE)
    flavor = conn.compute.find_flavor(FLAVOUR)
    keypair2 = conn.compute.find_keypair(KEYPAIR)
    network2 = conn.network.find_network(NETWORK)
    group = conn.network.find_security_group(GROUP)

    '''Creating the server'''

    server = conn.compute.find_server('zetksm1-web')
    if server is None:
           print("Creating the Web server")
           server = conn.compute.create_server(
            name ='zetksm1-web',
            image_id=image.id,
            flavor_id=flavor.id,
            key_name=keypair2.name,
            networks=[{"uuid": conn.network.find_network(NETWORK).id}],
            security_groups=[{"sgid": group.id}]
         )
    else:
            print("Web server already exists")

    server2 = conn.compute.find_server('zetksm1-app')
    if server2 is None:
        print("Creating the App server")
        server2 = conn.compute.create_server(
                name='zetksm1-app',
                image_id=image.id,
                flavor_id=flavor.id,
                key_name=keypair2.name,
                networks=[{"uuid": conn.network.find_network(NETWORK).id}],
                security_groups=[{"sgid": group.id}]
                )
    else:
        print("App server already exists")

    server3 = conn.compute.find_server('zetksm1-db')
    if server3 is None:
        print("Creating the DB server")
        server3 = conn.compute.create_server(
                name='zetksm1-db',
                image_id=image.id,
                flavor_id=flavor.id,
                key_name=keypair2.name,
                networks=[{"uuid": conn.network.find_network(NETWORK).id}],
                security_groups=[{"sgid": group.id}]
                )
    else:
        print("DB server already exists")

        '''Assign the floating IP'''
        '''Could not assign floating IP, error somewhere in this code'''
        #server = conn.compute.find_server('zetksm1-web')
        #floating_ip = conn.network.create_ip(
        #floating_network_id=public_net.id)
        #conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    server_list = ['zetksm1-web', 'zetksm1-app', 'zetksm1-db']
    for serv in server_list:
        server = conn.compute.find_server(serv)
        if server is None:
            print("Attempted to start " + serv + " but it doesn't exist")
        else:
            if conn.compute.get_server(server).status != "ACTIVE":
                conn.compute.start_server(server)
                #conn.compute.wait_for_server(conn.compute.find_server(server))
            else:
                print(serv + " is already active")
        
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    server_list = ['zetksm1-web', 'zetksm1-app', 'zetksm1-db']
    for serv in server_list:
        server = conn.compute.find_server(serv)
        if server is None:
            print(serv + "not found")
        else:
            if conn.compute.get_server(server).status == "ACTIVE":
                conn.compute.stop_server(server)
                print(serv + " has been stopped successfully")
            else:
                print(serv + " is not active so has not been changed")
    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    server_list = ['zetksm1-web', 'zetksm1-app', 'zetksm1-db']
    for serv in server_list:
        server = conn.compute.find_server(serv)
        if server is None:
            print(serv + " server already does not exist")
        else:
            conn.compute.delete_server(server)
            print(serv + "server has been deleted")

    zetksm1_rtr = conn.network.find_router('zetksm1-rtr')
    if zetksm1_rtr is None:
        print("router already does not exist")
    else:
        conn.network.delete_router(zetksm1_rtr)
        print("router has been deleted")
    
    time.sleep(5)
    zetksm1_subnet = conn.network.find_subnet('zetksm1-subnet')
    if zetksm1_subnet is None:
        print("subnet already does not exist")
    else:
        conn.network.delete_subnet(zetksm1_subnet)
        print("subnet has been deleted")

    zetksm1_network = conn.network.find_network('zetksm1-network')
    if zetksm1_network is None:
        print("network already does not exist")
    else:
        conn.network.delete_network(zetksm1_network)
        print("network has been deleted")
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    server_list = ['zetksm1-web', 'zetksm1-app', 'zetksm1-db']
    for serv in server_list:
        server = conn.compute.find_server(serv)
        if server is None:
            print(serv + " was not found")
        else:
            server = conn.compute.get_server(server)
            status = server.status
            print(serv + " status is " + status)
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
