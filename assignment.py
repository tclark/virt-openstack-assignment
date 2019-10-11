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
            name='woodjj1-subnet',
            network_id=network.id,
            ip_version='4',
            cidr=SUBNET
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
        print("Router resource created")

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
            print("Server [" + server + "] created")

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
