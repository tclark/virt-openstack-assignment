import argparse
import openstack
import time # Just for some delay during destory function

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

    # Check every server with names inside SERVERLIST list
    # and turn its status to ACTIVE when it is SHUTOFF
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
            print("Server [" + server + "] does not exist")

    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''

    # Check every server with names inside SERVERLIST list
    # and turn its status to SHUTOFF when it is ACTIVE
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
    
    # Find network, subnet and router first
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet('leejh2-subnet')
    router = conn.network.find_router('leejh2-rtr')

    # Check every server with names inside SERVERLIST list
    # and delete those servers if they exist 
    print("Destroying all servers in progress......")
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)

        # If server name is [leejh2-web], remove and delete floating IP
        # before deletion of [leejh2-web] server
        if check_server:
            if server == 'leejh2-web':
                web_server = conn.compute.get_server(check_server)
                web_floating_ip = web_server["addresses"][NETWORK][1]["addr"]

                print("Disassociate floating IP from WEB server......")
                conn.compute.remove_floating_ip_from_server(web_server, web_floating_ip)

                check_ip = conn.network.find_ip(web_floating_ip)
                conn.network.delete_ip(check_ip)
                print("Floating IP Released")

            conn.compute.delete_server(check_server)
            print("Server [" + server + "] has been destroyed")
        else:
            print("Server [" + server + "] is not existing")

    # Wait 5 seconds for servers to be deleted completely
    time.sleep(5)

    # If router exists, delete it
    print("Destroying router in progress......")
    if router:
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(router)
        print("Router has been destroyed")
    else:
        print("Router does not exist")

    # If subnet exists, delete it
    print("Destroying subnet in progress......")
    if subnet:
        conn.network.delete_subnet(subnet)
        print("Subnet has been destroyed")
    else:
        print("Subnet does not exist")

    # If network exists, delete it
    print("Destroying network in progress......")
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

    # Check every server name inside SERVERLIST
    # and display their status if they exist
    for server in SERVERLIST:
        check_server = conn.compute.find_server(server)

        if check_server:
            check_server = conn.compute.get_server(check_server)
            check_server_ip = check_server["addresses"][NETWORK][0]["addr"]

            # If server name is [leejh2-web] which has floating IP associated,
            # display its floating IP as well
            if server == 'leejh2-web':
                check_server_floating_ip = check_server["addresses"][NETWORK][1]["addr"]
            else:
                check_server_floating_ip = "Not Available"
            
            print("======================================")
            print("Server Name: [" + server + "]")
            print("Server IP: [" + check_server_ip + "]")
            print("Server Floating IP: [" + check_server_floating_ip + "]")
            print("Server Status: [" + check_server.status + "]")
            print("======================================")
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

    action = operations.get(operation, lambda: print('{}: no such operation'.format(operation)))
    action()
