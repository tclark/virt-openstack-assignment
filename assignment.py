"""
Author: James Grigg
"""

import argparse
import openstack

conn = openstack.connect(cloud_name='openstack')
public_net = conn.network.find_network('public-net')

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'grigjm1-net'
KEYPAIR = 'grigjm1-key'
SECURITY = 'assignment2'
SUBNET = '192.168.50.0/24'
SERVERLIST = { 'grigjm1-web', 'grigjm1-app', 'grigjm1-db' }

def create():
    ''' Create a set of Openstack resources '''
	
	# Find network, subnet and router first
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet('grigjm1-subnet')
    router = conn.network.find_router('grigjm1-rtr')

    # Create network if it is not found
    if network:
        print("Network resource already exist")
    else:
        network = conn.network.create_network(name=NETWORK)
        print("Network resource created")
		
    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
	
	# Check every server with names inside SERVERLIST list
    # and turn its status to ACTIVE when it is SHUTOFF
	
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)
        if check_server:
            check_server = conn.compute.get_server(check_server)
            if check_server.status == "ACTIVE":
                print("Server [" + server + "] is already active")
            elif check_server.status == "SHUTOFF":
                print("Server [" + server + "] is not active")
                print("Starting server [" + server + "]......")
                conn.compute.start_server(check_server)
                print("Server [" + server + "] is active")
        else:
            print("Server [" + server + "] does not exist")
			
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
