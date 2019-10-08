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

    # Find network, subnet and router first
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet('leejh2-subnet')
    router = conn.network.find_router('leejh2-rtr')

    # Create network when its name can not be found on catalyst cloud
    if network:
        print("Network resource already exist")
    else:
        network = conn.network.create_network(
            name=NETWORK
        )
        print("Network resource created")

    # Create subnet when its name can not be found on catalyst cloud
    if subnet:
        print("Subnet resource alreeady exist")
    else:
        subnet = conn.network.create_subnet(
            name='leejh2-subnet',
            network_id=network.id,
            ip_version='4',
            cidr=SUBNET
        )
        print("Subnet resource created")

    # Create router when its name can not be found on catalyst cloud
    if router:
        print("Router resource already exist")
    else:
        router = conn.network.create_router(
            name='leejh2-rtr',
            external_gateway_info={'network_id': public_net.id})
        conn.network.add_interface_to_router(router, subnet.id)
        print("Router resource created")

    # Find image for OS, flavour, authentication keypair and security group
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security = conn.network.find_security_group(SECURITY)

    # Create servers in SERVERLIST list, when servers with same name do not exist on catalyst cloud
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)
        if check_server:
            print("Servers are already existing")
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
            print("Server [" + server + "] has been created")

            # If server name in SERVERLIST is [leejh2-web], associate it with floating IP
            if server == 'leejh2-web':
                print("Associate floating IP address to WEB server......")
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
                web_server = conn.compute.find_server('leejh2-web')
                conn.compute.add_floating_ip_to_server(web_server, floating_ip.floating_ip_address)
                print("Floating IP allocated to WEB server")

    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''

    print("Checking all servers on progress......")

    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)
        if check_server:
            check_server = conn.compute.get_server(check_server)
            if check_server.status == "ACTIVE":
                print("Server [" + server + "] is already active")
            elif check_server.status == "SHUTOFF":
                print("Server [" + server + "] is currently deactived")
                print("Starting server [" + server + "]......")
                conn.compute.start_server(check_server)
                print("Server [" + server + "] is active")
        else:
            print("Server [" + server + "] is not existing")

    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''

    print("Checking all servers on progress......")

    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)
        if check_server:
            check_server = conn.compute.get_server(check_server)
            if check_server.status == "ACTIVE":
                print("Server [" + server + "] is currently active")
                print("Starting server [" + server + "]......")
                conn.compute.stop_server(check_server)
                print("Server [" + server + "] is deactived")
            elif check_server.status == "SHUTOFF":
                print("Server [" + server + "] is already shut down")
        else:
            print("Server [" + server + "] is not existing")
    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''

    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)
        if check_server:
            conn.compute.delete_server(check_server)
            conn.compute.wait_for_server(check_server)
            print("Server [" + server + "] has been destroyed")
        else:
            print("Server [" + server + "] is not existing")

    

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
