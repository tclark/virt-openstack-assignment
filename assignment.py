import argparse
import openstack

conn = openstack.connect(cloud_name='openstack')

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'leejh2-net'
KEYPAIR = 'leejh2-key'
SECURITY = 'assignment2'
SUBNET = '192.168.50.0/24'
SERVERLIST = { 'leejh2-web', 'leejh2-app', 'leejh2-db' }

public_net = conn.network.find_network('public-net')

def create():
    ''' Create a set of Openstack resources '''

    print("Creating resources on progress......")

    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet(SUBNET)
    router = conn.network.find_router('leejh2-rtr')

    if network:
        print("Network resource already exist")
    else:
        network = conn.network.create_network(
            name=NETWORK
        )
        print("Network resource created")

    if subnet:
        print("Subnet resource alreeady exist")
    else:
        subnet = conn.network.create_subnet(
            name='leejh2-subnet',
            network_id=network,
            ip_version='4',
            cidr=SUBNET
        )
        print("Subnet resource created")

    if router:
        print("Router resource already exist")
    else:
        router = conn.network.create_router(
            name='leejh2-rtr',
            external_gateway_info={'network_id': public_net.id})
        conn.network.add_interface_to_router(router)
        print("Router resource created")

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security = conn.compute.find_security_group(SECURITY)

    for server in SERVERLIST:
        check_server = conn.compute.find_server(name_or_id=server)
        if check_server:
            if check_server == 'leejh2-web':
                print("Associate floating IP address to WEB server")
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
                conn.compute.add_floating_ip_to_server(check_server, floating_ip.floating_ip_address)
                print("Floating IP allocated to WEB server")
            else:
                print("Floating IP aleeady allocated to WEB server")
        else:
            new_server = conn.compute.create_server(
                name=server,
                image_id=image.id,
                flavor_id=flavour.id,
                networks=[{"uuid": network.id}],
                key_name=keypair.name,
                security_groups=[{"name": security}]
            )
            new_server = conn.compute.wait_for_server(new_server)
            print("Server [" + server + "] has been created")

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
