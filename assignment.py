import argparse
import openstack

IMAGE = 'ubuntu-minimal-22.04-x86_64'
FLAVOUR = 'c1.c1r1'
PUBLIC_NETWORK = 'public-net'
NETWORK = 'nichmr1-net'
SUBNET = 'nichmr1-subnet'
ROUTER = 'nichmr1-rtr'
SECURITY_GROUP = 'assignment2'
KEYPAIR = 'nichmr1-key'
SERVERS = ['nichmr1-web','nichmr1-app', 'nichmr1-db']


def create():
    ''' Create a set of Openstack resources '''
    #Establish a connection to catalystcloud
    conn = openstack.connect(cloud_name='catalystcloud')
    
    #Create a network
    if conn.network.find_network(NETWORK) is None:
        network = conn.network.create_network(
            name = NETWORK
        )
        print('Network ' + NETWORK + ' created')
    else:
        network = conn.network.find_network(NETWORK)
        print('Network ' + NETWORK + ' already exists! Continuing...')

    #Create a subnet
    if conn.network.find_subnet(SUBNET) is None:
        subnet = conn.network.create_subnet(
            name = SUBNET,
            network_id = network.id,
            ip_version = '4',
            cidr = '192.168.50.0/24',
            gateway_ip = '192.168.50.1'
            )
        print('Subnet ' + SUBNET + ' created')
    else:
        print('Subnet ' + SUBNET + ' already exists! Continuing...')

    #Create a router
    public_network = conn.network.find_network(PUBLIC_NETWORK)
    if conn.network.find_router(ROUTER) is None:
        router = conn.network.create_router(
            name = ROUTER,
            external_gateway_info={'network_id': public_network.id}            
            )
        conn.network.add_interface_to_router(router, subnet.id)
        print('Router ' + ROUTER + ' created')
    else:
        print('Router ' + ROUTER + ' already exists! Continuing...')

    #Create three servers
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security_group = conn.network.find_security_group(SECURITY_GROUP)
    
    for server in SERVERS:
        if conn.compute.find_server(name_or_id=server)is None:
            new_server = conn.compute.create_server(
                    name = server,
                    image_id = image.id,
                    flavor_id = flavour.id,
                    networks=[{"uuid": network.id}], 
                    key_name=keypair.name,
                    security_groups=[{"name":security_group.name}]
                    )
            new_server = conn.compute.wait_for_server(new_server)
            print(server + " created")
            
            #The web server need a floating IP associated with it
            if server == 'nichmr1-web':
                #Create a floating IP address
                floating_ip = conn.network.create_ip(
                    floating_network_id=public_network.id
                )
                print("Floating IP created")
                #Associate the floating IP to the web server
                web_server = conn.compute.find_server('nichmr1-web')
                conn.compute.add_floating_ip_to_server(web_server, floating_ip.floating_ip_address)
                print("Assigned floating IP to web server")
        else:
            print("Server " + server + " already exists! Continuing...")


def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    conn = openstack.connect(cloud_name='catalystcloud')
    for server in SERVERS:
        if conn.compute.find_server(name_or_id=server) is not None:
            server_to_run = conn.compute.find_server(name_or_id=server)
            if conn.compute.get_server(server_to_run).status == 'SHUTOFF':
                conn.compute.start_server(server_to_run)
                print('Server ' + server + ' had been started')
            else:
                print('Server ' + server + ' is already running! Continuing...')
        else:
            print('Server ' + server + ' does not exist! Continuing...')

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    conn = openstack.connect(cloud_name='catalystcloud')
    for server in SERVERS:
        if conn.compute.find_server(name_or_id=server) is not None:
            server_to_run = conn.compute.find_server(name_or_id=server)
            if conn.compute.get_server(server_to_run).status == 'ACTIVE':
                conn.compute.stop_server(server_to_run)
                print('Server ' + server + ' had been stopped')
            else:
                print('Server ' + server + ' is already stopped! Continuing...')
        else:
            print('Server ' + server + ' does not exist! Continuing...')

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    conn = openstack.connect(cloud_name='catalystcloud')
    
    #Get the stuff to delete
    network = conn.network.find_network(NETWORK)
    router = conn.network.find_router(ROUTER)
    subnet = conn.network.find_subnet(SUBNET)

    #Destroy the Servers
    for server in SERVERS:
        if conn.compute.find_server(name_or_id=server) is not None:
            server_to_delete = conn.compute.find_server(name_or_id=server)
            #Destroy Floating IP
            if server == 'nichmr1-web':
                conn.network.delete_ip(
                        conn.network.find_ip(
                            conn.compute.get_server(server_to_delete).addresses['nichmr1-net'][1]["addr"]))
            conn.compute.delete_server(server_to_delete)
            print(server + " Destroyed")
        else:
            print("ERROR: " + server + " does not exist. Continuing...")


    #Destroy the Router
    if router is not None:
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(router)
        print('Router Destroyed')
    else:
        print("ERROR: Router does not exist. Continuing...")

    #Destroy the Subnet
    if subnet is not None:
        conn.network.delete_subnet(subnet, ignore_missing=False)
        print('Subnets Destroyed')
    else:
        print("ERROR: Subnet does not exist. Continuing...")


    #Destroy the Network
    if network is not None:
        conn.network.delete_network(network, ignore_missing=False)
        print('Network Destroyed')
    else:
        print("ERROR: Network does not exist. Continuing...")



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
