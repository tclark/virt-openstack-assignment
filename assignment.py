#!/usr/bin/env python

import argparse
import openstack

conn = openstack.connect(cloud_name='openstack')

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'woodjj1-net'
KEYPAIR = 'woodjj1-key'
SECURITY = 'assignment2'
SUBNET = 'woody-subnet'
ROUTER = 'woody-rtr'
SERVERLIST = [ 'woodjj1-web', 'woodjj1-app', 'woodjj1-db' ]

public_net = conn.network.find_network('public-net')

def create():
    ''' Create a set of Openstack resources '''

    #Create Network
    print("Creating Network......")

    # Finding network, subnet and router
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet(SUBNET)
    router = conn.network.find_router(ROUTER)

    # Create network if it doesn't exist
    if network:
        print("Network already exists")
    else:
        network = conn.network.create_network(
            name=NETWORK
        )
        print("Network created")

    # Create subnet if it doesn't exist
    if subnet:
        print("Subnet already exists")
    else:
        subnet = conn.network.create_subnet(
            name=SUBNET,
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1'
        )
        print("Subnet created")

   # Create router if it doesn't exist
    if router:
        print("Router already exists")
    else:
        router = conn.network.create_router(
            name='woodjj1-rtr',
            external_gateway_info={'network_id': public_net.id})
        conn.network.add_interface_to_router(router, subnet.id)
        print("Router created")
        
     # Launch Instances
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security = conn.network.find_security_group(SECURITY)

    # Create servers if they don't exist
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)
        if check_server:
            print("Servers already exist")
            
        else:
            new_server = conn.compute.create_server(
                name=server,
                image_id=image.id,
                flavor_id=flavour.id,
                networks=[{"uuid": network.id}],
                key_name=keypair.name,
                security_groups=[{"name": security.name}]
            )
            new_server = conn.compute.wait_for_server(new_server)
            print(" [" + server + "] server created")

            # Associate Floating IP address to woodjj1-web
            if server == 'woodjj1-web':
                print("Associating floating IP address to WEB server......")
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
                web_server = conn.compute.find_server('woodjj1-web')
                conn.compute.add_floating_ip_to_server(web_server, floating_ip.floating_ip_address)
                print("Floating IP address has been allocated to WEB server")

    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    # Check SERVERLIST for servers and set status to ACTIVE if servers not running
    print("Checking servers......")
    for server in SERVERLIST:
            check_server = conn.compute.find_server(server)
            if check_server:
                check_server = conn.compute.get_server(check_server)
            if check_server.status == "ACTIVE":
                print(" [" + server + "] server is currently active")
            elif check_server.status == "SHUTOFF":
                print(" [" + server + "] server is currently shutoff")
                print("Starting [" + server + "]  server......")
                conn.compute.start_server(check_server)
                print(" [" + server + "] server is active")

    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    # Check SERVERLIST for servers and set status to SHUTOFF if servers are running
    print("Checking all servers on progress......")
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)
        if check_server:
            check_server = conn.compute.get_server(check_server)
            if check_server.status == "ACTIVE":
                print(" [" + server + "] server is currently active")
                print("Starting [" + server + "] server......")
                conn.compute.stop_server(check_server)
                print(" [" + server + "] server is not running")
            elif check_server.status == "SHUTOFF":
                print(" [" + server + "] is already shut down")

    pass

def destroy():
    ''' Tear down the set of Openstack resources
    produced by the create action
    '''

    # Find network, subnet and router first
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet('woodjj1-subnet')
    router = conn.network.find_router('woodjj1-rtr')

    # Check SERVERLIST for servers and destroy servers if they exist
    print("Destroying all servers.....")
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)

        # Release floating IP before destroying woodjj1-web server
        if check_server:
             check_server = con.compute.get_server(check_server)
             if server == 'woodjj1-web':
                web_server = conn.compute.get_server(check_server)
                web_floating_ip = web_server["addresses"][NETWORK][1]["addr"]

                print("Disassociate floating IP from WEB server......")
                conn.compute.remove_floating_ip_from_server(web_server, web_floating_ip)

                check_ip = conn.network.find_ip(web_floating_ip)
                conn.network.delete_ip(check_ip)
                print("Floating IP Released")

                conn.compute.delete_server(check_server)
                print(" [" + server + "] server has been destroyed")
        else:
            print(" [" + server + "] server not found")

  # Destroy router if it exists
    print("Destroying router......")
    if router:
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(router)
        print("Router has been destroyed")
    else:
        print("Router does not exist")

    # Destroy subnet if it exists
    print("Destroying subnet......")
    if subnet:
        conn.network.delete_subnet(subnet)
        print("Subnet has been destroyed")
    else:
        print("Subnet does not exist")

    # Destroy network if it exists
    print("Destroying network......")
    if network:
        conn.network.delete_network(network)
        print("Network has been destroyed")
    else:
        print("Network does not exist")


    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    # Check SERVERLIST for servers and display status if they exist

    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)

        if check_server:
            check_server = conn.compute.get_server(check_server)
            check_server_ip = check_server["addresses"][NETWORK][0]["addr"]

            # Display IP and floating IP address of WEB server if it exists,
            if server == 'woodjj1-web':
                check_server_floating_ip = check_server["addresses"][NETWORK][1]["addr"]
            else:
                check_server_floating_ip = "Not found"            
            print("Server Name: [" + server + "]")
            print("Server IP: [" + check_server_ip + "]")
            print("Server Floating IP: [" + check_server_floating_ip + "]")
            print("Server Status: [" + check_server.status + "]")
        else:
            print("Server [" + server + "] does not exist")

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

    action = operations.get(operation, lambda:  print('{}: no such operation'.format(operation)))
    action()

