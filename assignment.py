import argparse
import openstack

conn = openstack.connect(cloud_name="catalystcloud")

IMAGE = "ubuntu-22.04-x86_64"
FLAVOUR = "c1.c1r1"
NETWORK = "huar2-net"
KEYPAIR = "huar2-key"
SUBNET = "huar2-subnet"
ROUTER = "huar2-router"
SECGROUP = "assignment2"

WEBSERVER = "huar2-web"
APPSERVER = "huar2-app"
DBSERVER = "huar2-db"
SERVERS = [WEBSERVER, APPSERVER, DBSERVER]

GATEWAYADDRESS = '192.168.50.1'

NEWLINE = "--------------------------------------------------------"

public_net = conn.network.find_network("public-net")

def create():
    ''' Create a set of Openstack resources '''
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    network = conn.network.find_network(NETWORK)
    router = conn.network.find_router(ROUTER)
    keypair = conn.compute.find_keypair(KEYPAIR)
    print(NEWLINE)
    if not network:
        print("Creating network: " + NETWORK)
        network = conn.network.create_network(name=NETWORK)
        print("Network " + NETWORK + " created")
        print("Creating subnet: " + SUBNET)
        subnet = conn.network.create_subnet(
        name=SUBNET,
        network_id=network.id,
        ip_version='4',
        cidr='192.168.50.0/24',
        gateway_ip=GATEWAYADDRESS)
        print("Subnet created")
    else:
        print("Network exists, therefore not created")
    print(NEWLINE)
    if not router:
        print("Creating router: " + ROUTER)
        router = conn.network.create_router(name=ROUTER, external_gateway_info={"network_id": public_net.id})
        conn.network.add_interface_to_router(router.id, subnet.id)
        print("Router created and attached to subnet: " + SUBNET)
    else:
        print("Router exists, therefore not created")
    for SERVERNAME in SERVERS:
        server = conn.compute.find_server(SERVERNAME)
        print(NEWLINE)
        if not server:
            server = conn.compute.create_server(name=SERVERNAME, image_id=image.id, flavor_id=flavour.id, networks=[{"uuid": network.id}], key_name=keypair.name, security_groups=[{"name": SECGROUP}])
            print("Creating VM: " + SERVERNAME)
            server = conn.compute.wait_for_server(server)
            print("VM Created")
            if SERVERNAME == WEBSERVER:
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
                print("Floating IP address: " + floating_ip.floating_ip_address)
                conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)
                print("Floating IP address added to " + SERVERNAME)
        else:
            print('Server "' + SERVERNAME + '" already exists, no action taken')
    print(NEWLINE)
    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    for SERVERNAME in SERVERS:
        server = conn.compute.find_server(SERVERNAME)
        print(NEWLINE)
        print('Server: ' + SERVERNAME)
        if server:
            serverDetails = conn.compute.get_server(server)
            serverStatus = serverDetails.status
            print("Current status: " + serverStatus)
            if serverStatus == "SHUTOFF":
                conn.compute.start_server(serverDetails)
                print("Starting server")
                conn.compute.wait_for_server(serverDetails, status='ACTIVE')
                print("Server started")
                serverDetails = conn.compute.get_server(server)
                serverStatus = serverDetails.status
                print("New status: " + serverStatus)
            else:
                print("Server already active, no action taken")
        else:
            print("Server not found, no action taken")
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    for SERVERNAME in SERVERS:
        server = conn.compute.find_server(SERVERNAME)
        print(NEWLINE)
        print('Server: ' + SERVERNAME)
        if server:
            serverDetails = conn.compute.get_server(server)
            serverStatus = serverDetails.status
            print("Current status: " + serverStatus)
            if serverStatus == "ACTIVE":
                conn.compute.stop_server(serverDetails)
                print("Server stopping")
                conn.compute.wait_for_server(serverDetails, status='SHUTOFF')
                print("Server stopped")
                serverDetails = conn.compute.get_server(server)
                serverStatus = serverDetails.status
                print("New status: " + serverStatus)        
            elif serverStatus == "SHUTOFF":
                print("Server already stopped, no action taken")
        else:
            print("Server not found, no action taken")
    print(NEWLINE)
    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    for SERVERNAME in SERVERS:
        SERVER = conn.compute.find_server(SERVERNAME)
        print(NEWLINE)
        print('Server: ' + SERVERNAME)
        if SERVER:
            server = conn.compute.get_server(SERVER)
            if SERVERNAME == WEBSERVER:
                floating_ip = server["addresses"][NETWORK][1]["addr"]
                print("Disallowcating floating IP " + floating_ip + " from " + SERVERNAME)
                conn.compute.remove_floating_ip_from_server(server, floating_ip)
                ip_address = conn.network.find_ip(floating_ip)
                conn.network.delete_ip(ip_address)
                print("Floating IP address " + floating_ip + " released")
            conn.compute.delete_server(SERVER)
            print('Server deleted')
        else:
            print("Server not found, therefore no action taken")
    network = conn.network.find_network(NETWORK)
    router = conn.network.find_router(ROUTER)
    subnet = conn.network.find_subnet(SUBNET)
    print(NEWLINE)
    if network and subnet:
        ports = conn.network.ports(network_id=network.id, subnet_id=subnet.id, ip_address=GATEWAYADDRESS)
        if ports:
            print("Deleting ports from subnet")
            for port in ports:
                if port.fixed_ips[0]['ip_address'] == GATEWAYADDRESS:
                    print("Removing interface from router")
                    conn.network.remove_interface_from_router(router, subnet_id=subnet.id, port_id=port.id)
                    print("Interface removed")
                else:
                    conn.network.delete_port(port.id, ignore_missing=True)
        else:
            print("Ports not found")
    if router:
        print("Deleting router " + ROUTER)
        conn.network.delete_router(router)
        print("Router deleted")
    else:
        print('Router "' + ROUTER + '" not found')
    if subnet:
        print("Deleting subnet ID: " + subnet.id)
        conn.network.delete_subnet(subnet, ignore_missing=False)
        print("Subnet deleted")
    else:
        print('Subnet "' + SUBNET + '" not found')
    print(NEWLINE)
    if network:
        conn.network.delete_network(network, ignore_missing=False)
        print("Network " + NETWORK + " deleted")
    else:
        print('Network "' + NETWORK + '" not found')
    print(NEWLINE)
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    for SERVERNAME in SERVERS:
        server = conn.compute.find_server(SERVERNAME)
        if server:
            serverDetails = conn.compute.get_server(server)
            private_ip = server["addresses"][NETWORK][0]["addr"]
            if SERVERNAME == WEBSERVER:
                floating_ip = server["addresses"][NETWORK][1]["addr"]
            else:
                floating_ip = "no floating IP"
            serverStatus = serverDetails.status
            print(NEWLINE)
            print("Server name: " + SERVERNAME)
            print("Current status: " + serverStatus)
            print("Private IP: " + private_ip)
            print("Floating IP: " + floating_ip)
        else:
            print('Server "' + SERVERNAME + '" not found')
    print(NEWLINE)
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
