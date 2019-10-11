'''
Author: James Grigg
Due Date: 14th October 2019

Resources:
https://docs.openstack.org/openstacksdk/latest/user/index.html
https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
https://docs.openstack.org/openstacksdk/latest/user/connection.html
https://docs.openstack.org/openstacksdk/latest/user/guides/network.html
In Class Material
'''

import argparse
import openstack

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'grigjm1-net'
KEYPAIR = 'grigjm1-key'
SECURITY = 'assignment2'
PUBLICNET_NAME = 'public-net'
CLOUD_NAME = 'openstack'
SUBNET = '192.168.50.0/24'
SERVERLIST = { 'grigjm1-web', 'grigjm1-app', 'grigjm1-db' }

conn = openstack.connect(cloud_name=CLOUD_NAME)
public_net = conn.network.find_network(PUBLICNET_NAME)

#The CREATE method is used to create the network, subnet and router
#It will check to see if any of the resources exist before creating them
#It will assign a floating ip to the web server
def create():
    ''' Create a set of Openstack resources '''
	
	#Find network, subnet and router first
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet('grigjm1-subnet')
    router = conn.network.find_router('grigjm1-rtr')

    #Create network if it is not found
    if network:
        print("Error: Network exists")
    else:
        network = conn.network.create_network(name=NETWORK)
        print("Network created!")
		
		
	#Create subnet if it is not found
    if subnet:
        print("Error: Subnet exists")
		
    else:
        subnet = conn.network.create_subnet(
            name='grigjm1-subnet',
            network_id=network.id,
            ip_version='4',
            cidr=SUBNET
        )
        print("Subnet created!")
		

    #Create router if it is not found
    if router:
        print("Error: Router exists")
		
    else:
        router = conn.network.create_router(
            name='grigjm1-rtr',
            external_gateway_info={'network_id': public_net.id})
        conn.network.add_interface_to_router(router, subnet.id)
        print("Router created!")
		

    #Find the required resources
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security = conn.network.find_security_group(SECURITY)

    #Create servers in the server list (SERVERLIST), if they are not found
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)
        if check_server:
            print("Error: Server(s) already exist!")
			
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
            print("Server: " + server + " has been created!")

			#If a server exists with the name "grigjm1-web", give it floating ip
            if server == 'grigjm1-web':
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
                web_server = conn.compute.find_server('grigjm1-web')
                conn.compute.add_floating_ip_to_server(web_server, floating_ip.floating_ip_address)
                print("Web server has been allocated floating ip!")
		
    pass

#The RUN method is used to start up the servers
#It will inform the user if any of the servers do not eist or if they are already running
def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
	
	#Change every SHUTOFF server in the server list to be ACTIVE
	
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)
        if check_server:
            check_server = conn.compute.get_server(check_server)
            if check_server.status == "ACTIVE":
                print("Server: " + server + " is already active!")
            elif check_server.status == "SHUTOFF":
                print("Starting server " + server + "")
                conn.compute.start_server(check_server)
                print("Server: " + server + " is now active!")
        else:
            print("Server: " + server + " does not exist")
			
    pass

#The STOP method is used to stop the servers
#It will inform the user if any of the servers do not exist
def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
	
	#Works similarily to the run method
	#Change every ACTIVE server in the server list to be SHUTOFF 
    print("Checking all servers on progress......")
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)
        if check_server:
            check_server = conn.compute.get_server(check_server)
            if check_server.status == "ACTIVE":
                conn.compute.stop_server(check_server)
                print("Server: " + server + " is shutoff!")
            elif check_server.status == "SHUTOFF":
                print("Server: " + server + " is already shut down!")
        else:
            print("Server: " + server + " does not exist!")
    pass

#The DESTROY method is used to destroy the created resources
#It will ignore any non created resources
def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    
    #Find required resources
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet('grigjm1-subnet')
    router = conn.network.find_router('grigjm1-rtr')
	
	#Delete all servers with names inside the server list 
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)

        #Remove floating ip off the "grigjm1-web" server (if it exists)
        if check_server:
            if server == 'grigjm1-web':
                web_server = conn.compute.get_server(check_server)
                web_floating_ip = web_server["addresses"][NETWORK][1]["addr"]
                conn.compute.remove_floating_ip_from_server(web_server, web_floating_ip)
                check_ip = conn.network.find_ip(web_floating_ip)
                conn.network.delete_ip(check_ip)
                print("Floating IP removed!")

            conn.compute.delete_server(check_server)
            print("Server: " + server + " has been destroyed!")
        else:
            print("Server: " + server + " does not exist!")

    #Delete subnet if it already exists
    if subnet:
        conn.network.delete_subnet(subnet)
        print("Subnet has been destroyed!")
    else:
        print("Subnet does not exist!")

    #Delete network if it already exists
    if network:
        conn.network.delete_network(network)
        print("Network has been destroyed!")
    else:
        print("Network does not exist!")
		
	#Delete router if it already exists
    if router:
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(router)
        print("Router has been destroyed!")
    else:
        print("Router does not exist!")

    pass

#The STATUS method is used to find out the status of the created servers
#If a floating ip exists, it will print that as well
def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''

	#Display the status for any existing servers in the server list
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)

        if check_server:
            check_server = conn.compute.get_server(check_server)
            check_server_ip = check_server["addresses"][NETWORK][0]["addr"]

            #Display floating ip for "grigjm1-web" server
            if server == 'grigjm1-web':
                check_server_floating_ip = check_server["addresses"][NETWORK][1]["addr"]
            else:
                check_server_floating_ip = "Not Available"
            
            print("Name: " + server + "")
            print("IP: " + check_server_ip + "")
            print("Floating IP: " + check_server_floating_ip + "")
            print("Status: " + check_server.status + "")
        else:
            print("Server: " + server + " does not exist")
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
