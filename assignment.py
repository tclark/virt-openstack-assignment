import argparse
import openstack

conn = openstack.connect(cloud_name="catalystcloud")

IMAGE = "ubuntu-22.04-x86_64"
FLAVOUR = "c1.c1r1"
NETWORK = "huar2-net"
KEYPAIR = "huar2-key"
SERVERNAME = "huar2-server"
SUBNET = "huar2-subnet"
ROUTER = "huar2-router"

WEBSERVER = "huar2-web"
APPSERVER = "huar2-server"
DBSERVER = "huar2-db"
SERVERS = [WEBSERVER, APPSERVER, DBSERVER]

public_net = conn.network.find_network("public-net")

def create():
    ''' Create a set of Openstack resources '''
    server = conn.compute.find_server(SERVERNAME)
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    network = conn.network.find_network(NETWORK)
    keypair = conn.compute.find_keypair(KEYPAIR)
    if not network:
        print("Creating network: " + NETWORK)
        new_network = conn.network.create_network(name=NETWORK)
        print("Network " + NETWORK + " created")
        print("Creating subnet: " + SUBNET)
        new_subnet = conn.network.create_subnet(
        name=SUBNET,
        network_id=new_network.id,
        ip_version='4',
        cidr='192.168.50.0/24',
        gateway_ip='192.168.50.1')
        print("Subnet created")
        new_router = conn.network.create_router(name=ROUTER, external_gateway_info={"network_id": public_net.id})
        conn.network.add_interface_to_router(new_router.id, new_subnet.id)
    else:
        print("Network not created")
    '''if not server:
        server = conn.compute.create_server(name=SERVERNAME, image_id=image.id, flavor_id=flavour.id, networks=[{"uuid": network.id}], key_name=keypair.name, security_groups=[{"name": "lab5-secgrp"}])
        print("Creating VM: " + SERVERNAME)
        server = conn.compute.wait_for_server(server)
        print("VM Created: " + SERVERNAME)

        public_net = conn.network.find_network("public-net")
        floating_ip = conn.network.create_ip(floating_network_id=public_net.id)

        print("Floating IP address: " + floating_ip.floating_ip_address)
        conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)
        print("Floating IP address added to " + SERVERNAME)
    else:
        print("Server already exists, no action taken")
    '''

    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    server = conn.compute.find_server(SERVERNAME)
    if server:
        serverDetails = conn.compute.get_server(server)
        serverStatus = serverDetails.status
        print("Current status: " + serverStatus)
        if serverStatus == "SHUTOFF":
            conn.compute.start_server(serverDetails)
            print("Starting server")
            conn.compute.wait_for_server(serverDetails, status='ACTIVE')
            print("Server started")
            serverDetails = conn.compute.get_server(server)
            serverStatus = serverDetails.status
            print("New status: " + serverStatus)
        else:
            print("Server already active, no action taken")
    else:
        print("Server not found")
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    server = conn.compute.find_server(SERVERNAME)
    if server:
        serverDetails = conn.compute.get_server(server)
        serverStatus = serverDetails.status
        print("Current status: " + serverStatus)
        if serverStatus == "ACTIVE":
            conn.compute.stop_server(serverDetails)
            print("Server stopping")
            conn.compute.wait_for_server(serverDetails, status='SHUTOFF')
            print("Server stopped")
            serverDetails = conn.compute.get_server(server)
            serverStatus = serverDetails.status
            print("New status: " + serverStatus)        
        else:
            print("Server already stopped, no action taken")
    else:
        print("Server not found")
    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    network = conn.network.find_network(NETWORK)

    for subnet in network.subnet_ids:
        print("Deleting subnet ID: " + subnet)
        conn.network.delete_subnet(subnet, ignore_missing=False)
    print("Deleting network: " + NETWORK)
    conn.network.delete_network(network, ignore_missing=False)
    print("Network " + NETWORK + " deleted")

    '''SERVER = conn.compute.find_server(SERVERNAME)
    
    if SERVER:
        server = conn.compute.get_server(SERVER)
        floating_ip = server["addresses"][NETWORK][1]["addr"]

        print("Disallowcating floating IP " + floating_ip + " from " + SERVERNAME)
        conn.compute.remove_floating_ip_from_server(server, floating_ip)

        server = conn.compute.delete_server(SERVER)
        print("Server deleted")

        ip_address=conn.network.find_ip(floating_ip)
        conn.network.delete_ip(ip_address)
        print("Floating IP address " + floating_ip + " released")
    else:
        print("Server not found")'''
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    server = conn.compute.find_server(SERVERNAME)
    if server:
        serverDetails = conn.compute.get_server(server)
        private_ip = server["addresses"][NETWORK][0]["addr"]
        if SERVERNAME == "huar2-server":
            floating_ip = server["addresses"][NETWORK][1]["addr"]
        else:
            floating_ip = "not found"
        serverStatus = serverDetails.status
        print("Server name: " + SERVERNAME)
        print("Current status: " + serverStatus)
        print("Private IP: " + private_ip)
        print("Floating IP: " + floating_ip)
    else:
        print("Server not found")
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
