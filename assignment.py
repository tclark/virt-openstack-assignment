import argparse
import openstack

IMAGE = 'ubuntu-minimal-22.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'nichmr1-net'
SECURITY_GROUP = 'assignment2'
KEYPAIR = 'nichmr1-key'
SERVERS = ['nichmr1-web','nichmr1-app', 'nichmr1-db']


def create():
    ''' Create a set of Openstack resources '''
    #Establish a connection to catalystcloud
    conn = openstack.connect(cloud_name='catalystcloud')
    
    #Create a network
    network = conn.network.create_network(
            name='nichmr1-net'
            )

    print('Network created')

    subnet = conn.network.create_subnet(
            name='nichmr1-subnet',
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1'
            )

    print('Subnet created')

    #Create a router
    public_network = conn.network.find_network('public-net')
    router = conn.network.create_router(
            name='nichmr1-rtr',
            external_gateway_info={'network_id': public_network.id}            
            )
    conn.network.add_interface_to_router(router, subnet.id)

    print('Router created')

    #Create a floating IP address
    floating_ip = conn.network.create_ip(
            floating_network_id=public_network.id
            )

    print('Floating IP created')

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

            if server == 'nichmr1-web':
                web_server = conn.compute.find_server('nichmr1-web')
                conn.compute.add_floating_ip_to_server(web_server, floating_ip.floating_ip_address)
                print("Assigned floating IP to web server")
        else:
            print("ERROR: " + server + " already exists!")


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
    conn = openstack.connect(cloud_name='catalystcloud')
    
    #Get the stuff to delete
    network = conn.network.find_network('nichmr1-net')
    router = conn.network.find_router('nichmr1-rtr')
    subnet = conn.network.find_subnet('nichmr1-subnet')

    #Destroy the Servers
    for server in SERVERS:
        if conn.compute.find_server(name_or_id=server) is not None:
            server_to_delete = conn.compute.find_server(name_or_id=server)
            #Remove and Destroy Floating IP
            if server == 'nichmr1-web':
                conn.network.delete_ip(conn.network.find_ip(conn.compute.get_server(server_to_delete).addresses['nichmr1-net'][1]["addr"]))
                #nichmr1_web = conn.compute.get_server(server_to_delete)
                #nichmr1_web_floating_ip = nichmr1_web['addresses'][network][1]['addr']
                #conn.compute.remove_floating_ip_from_server(nichmr1_web, nichmr1_web_floating_ip)
                #ip_to_delete = conn.network.find_ip(nichmr1_web_floating_ip)
                #conn.network.delete_ip(ip_to_delete, ignore_missing=False)
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
