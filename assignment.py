import argparse
import openstack
import time

conn = openstack.connect(cloud_name='openstack')

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'haycc1-net'
KEYPAIR = 'haycc1-key'
SUBNET = 'haycc1-sub'
ROUTER = 'haycc1-rtr'
CIDR = '192.168.50.0/24'
IP = '4'

SERVERNAMES = ['haycc1-web', 'haycc1-app', 'haycc1-db']

net = conn.network.find_network(NETWORK)
rtr = conn.network.find_router(ROUTER)
sub = conn.network.find_subnet(SUBNET)
public_net = conn.network.find_network('public-net')


def create():
    ''' Create a set of Openstack resources '''
    image = conn.compute.find_image(IMAGE)
    flavor = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security_group = conn.network.find_security_group('assignment2')
    
   
    print("Creating servers, this may take a few minutes...")
    # Network and Subnet creation
    if net is None:
        new_network = conn.network.create_network(name=NETWORK)
        print('Network created')
        new_subnet = conn.network.create_subnet(name=SUBNET, cidr=CIDR, network_id=new_network.id, ip_version=IP)
        print('Subnet created')
    else:
        print(f'Network already exists: {NETWORK}')

    # Router creation
    if rtr is None:
        new_router = conn.network.create_router(name=ROUTER, external_gateway_info={'network_id': public_net.id})
        conn.network.add_interface_to_router(new_router, new_subnet.id)
    else:
        print(f'Router already exists: {ROUTER}')


    # Server creation
    for name in SERVERNAMES:
        serverName = name
        if not conn.compute.find_server(name):
            server = conn.compute.create_server(name=serverName, image_id=image.id, flavor_id=flavor.id, networks=[{'uuid': new_network.id}], key_name=keypair.name, security_groups=[{'name':security_group.id}])
            server = conn.compute.wait_for_server(server)
            print(f'Server created: {name}')

            # Checking for the web server and adding a floating ip address to it
            if serverName == "haycc1-web":
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
                webServer = conn.compute.find_server("haycc1-web")
                conn.compute.add_floating_ip_to_server(webServer, floating_ip.floating_ip_address)
        else:
            print(f'Server already exists: {name}')

pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
   # Start servers if shutdown
    for name in SERVERNAMES:
        server = conn.compute.find_server(name_or_id=name)
        if server is not None:
            server = conn.compute.get_server(server)
            if server.status == "SHUTOFF":
                conn.compute.start_server(server)
                print(f'Server running: {name}')
            elif server.status == "ACTIVE":
                print(f'Server already running: {name}')
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    # Shutdown servers if running
    for name in SERVERNAMES:
        server = conn.compute.find_server(name_or_id=name)
        if server is not None:
            server = conn.compute.get_server(server)
            if server.status == "ACTIVE":
                conn.compute.stop_server(server)
                print(f'Server stopped: {name}')
            elif server.status == "SHUTOFF":
                print(f'Server already stopped: {name}')

    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''

        # Deletes all three servers including, router, network and subnet
    for name in SERVERNAMES:
        server = conn.compute.find_server(name_or_id=name)
        if server is not None:
            #Release floating IP from web server
            if name == 'haycc1-web':
                webServer = conn.compute.get_server(server)
                webFloatIP = webServer["addresses"][NETWORK][1]["addr"]
                conn.compute.remove_floating_ip_from_server(webServer, webFloatIP)
                getIP = conn.network.find_ip(webFloatIP)
                conn.network.delete_ip(getIP)
                print("Floating IP removed from the web server")


            conn.delete_server(server)
            #Gives enough time for the servers to delete
            time.sleep(3)
            print(f'Server deleted: {name}')
        else:
            print(f'Server already deleted: {name}')


    router = conn.network.find_router("haycc1-rtr")
    conn.network.remove_interface_from_router(router, sub.id)
    conn.network.delete_router(router)
    print(f"Router Destroyed")

    subnet = conn.network.find_subnet("haycc1-sub")
    conn.network.delete_subnet(subnet)
    print(f"Subnet Destroyed")

    network = conn.network.find_network("haycc1-net")
    conn.network.delete_network(network)
    print(f"Network Destroyed")
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    # Shows server names, current status and ip address
    for name in SERVERNAMES:
        server = conn.compute.find_server(name_or_id=name)
        if server is not None:
            svr = conn.compute.get_server(server)
            addresses = []
            for info in server.addresses[NETWORK]:
                addresses.append(info['addr'])
                print(f'Sever: {svr.name}, Status: {svr.status}, Address: {addresses}')
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
