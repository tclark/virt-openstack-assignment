import argparse
import openstack
import time

conn = openstack.connect(cloud_name='openstack')

def create():
    ''' Create a set of Openstack resources '''
	
    '''create network'''
    cooph3_network = conn.network.find_network('cooph3-net')
    if cooph3_network is None:
        cooph3_network = conn.network.create_network(name='cooph3-net')
        print("Network created")
    else:
        print("Network already exists")
	

    '''create subnet'''		
    cooph3_subnet = conn.network.find_subnet('cooph3-subnet')
    if cooph3_subnet is None:
        cooph3_subnet = conn.network.create_subnet(
        name='cooph3-subnet',
        network_id=cooph3_network.id,
        ip_version='4',
        cidr='192.168.50.0/24',
        gateway_ip='192.168.50.1')
        print("Subnet created")
    else:
        print("Subnet already exists")
		

    '''create router'''
    public_net = conn.network.find_network('public-net')
    cooph3_rtr = conn.network.find_router('cooph3-rtr')
    if cooph3_rtr is None:
        cooph3_rtr = conn.network.create_router(name='cooph3-rtr', admin_state_up=True, ext_gateway_net_id=public_net.id)
        print("Router created")
    else:
        print("Router already exists")


    '''create servers'''
    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'
    NETWORK = 'cooph3-net'
    KEYPAIR = 'cooph3-key'
    GROUP = 'assignment2'

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    network = conn.network.find_network(NETWORK)
    keypair = conn.compute.find_keypair(KEYPAIR)
    sec_group = conn.network.find_security_group(GROUP)
    server_list = ['cooph3-web', 'cooph3-app', 'cooph3-db']

    for serv in server_list:
        server = conn.compute.find_server(serv)
        if server is None:
            print("Creating " + serv + " server...")
            server = conn.compute.create_server(name=serv, image_id=image.id, flavor_id=flavour.id, networks=[{"uuid": network.id}], key_name=keypair.name)
            server = conn.compute.wait_for_server(server)
            conn.compute.add_security_group_to_server(server, sec_group)
            print(serv + " server created")
        else:
            print(serv + " server already exists")


    '''create and assign floating IP'''
    server = conn.compute.find_server('cooph3-web')
    floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
    conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)
    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    server_list = ['cooph3-web', 'cooph3-app', 'cooph3-db']
    for serv in server_list:
        server = conn.compute.find_server(serv)
        if server is None:
            print ("Error: Tried to start " + serv + " but it does not exist")
        else:
            try:
                conn.compute.start_server(server)
            except:
                print (serv + " is already ACTIVE")
            else:
                print (serv + " is ACTIVE")
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    server_list = ['cooph3-web', 'cooph3-app', 'cooph3-db']
    for serv in server_list:
        server = conn.compute.find_server(serv)
        if server is None:
            print ("Error: Tried to stop " + serv + " but it does not exist")
        else:
            try:
                conn.compute.stop_server(server)
            except:
                print (serv + " is already SHUTOFF")
            else:
                print (serv + " is SHUTOFF")
    pass

def destroy():
    ''' Tear down the set of Openstack resources
    produced by the create action
    '''
    server_list = ['cooph3-web', 'cooph3-app', 'cooph3-db']
    for serv in server_list:
        server = conn.compute.find_server(serv)
        if server is None:
            print(serv + " server already does not exist")
        else:
            conn.compute.delete_server(server)
            print(serv + "server has been deleted")

    cooph3_rtr = conn.network.find_router('cooph3-rtr')
    if cooph3_rtr is None:
        print("router already does not exist")
    else:
        conn.network.delete_router(cooph3_rtr)
        print("router has been deleted")

    time.sleep(5)
    cooph3_subnet = conn.network.find_subnet('cooph3-subnet')
    if cooph3_subnet is None:
        print("subnet already does not exist")
    else:
        conn.network.delete_subnet(cooph3_subnet)
        print("subnet has been deleted")

    cooph3_network = conn.network.find_network('cooph3-net')
    if cooph3_network is None:
        print("network already does not exist")
    else:
        conn.network.delete_network(cooph3_network)
        print("network has been deleted")
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    server_list = ['cooph3-web', 'cooph3-app', 'cooph3-db']
    for serv in server_list:
        server = conn.compute.find_server(serv)
        if server is None:
            print (serv + " does not exist so there are no available details")
        else:
            gotserver = conn.compute.get_server(server)
            status = gotserver.status
            print(serv + "is currently " + status)
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
