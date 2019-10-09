import argparse
import openstack
import time

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'jonear2-net'
SUBNET = 'jonear2-subnet'
ROUTER = 'jonear2-rtr'
KEYPAIR = 'jonear2-key'
SECURITY_GRP = 'assignment2'
serverNames = ['jonear2-web', 'jonear2-app', 'jonear2-db']

#Connect to openstack
conn = openstack.connect(cloud_name='openstack')


def create():
    ''' Create a set of Openstack resources '''
    #Get already created resources
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    network = conn.network.find_network(NETWORK)
    router = conn.network.find_router(ROUTER)

    #Create network
    if not network:
        print("Creating network...")
        network = conn.network.create_network(name=NETWORK)
        subnet = conn.network.create_subnet(
            name=SUBNET,
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1')
        print("Network created successfully")
    else:
        print("Network already created")
    
    #Create router
    if not router:
        print("Creating router...")
        public = conn.network.find_network('public-net')
        attrs = {'name': ROUTER, 'external_gateway_info': {'network_id': public.id}}
        router = conn.network.create_router(**attrs)
        network = conn.network.find_network(NETWORK)
        conn.network.add_interface_to_router(router, subnet_id=network.subnet_ids[0])
        print("Router created successfully")
    else:
        print("Router already created")
 
    #Create servers
    conn.network.add_interface_to_router(router, subnet_id=network.subnet_ids[0])
    for name in serverNames:
        if not conn.compute.find_server(name):
            print("Creating %s server..." % name)
            server = conn.compute.create_server(name=name, image_id=image.id, flavor_id=flavour.id, networks=[{"uuid": network.id}], key_name=keypair.name)
            conn.compute.wait_for_server(server)
            if name is serverNames[0]:
                floatingIP=conn.network.create_ip(floating_network_id=conn.network.find_network('public-net').id)
                conn.compute.add_floating_ip_to_server(server, address=floatingIP.floating_ip_address)
            security_grp = conn.network.find_security_group(SECURITY_GRP)
            conn.compute.add_security_group_to_server(server, security_grp)
            print("%s server create successfully" % name)
        else:
            print("%s server already created" % name)

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    for name in serverNames:
        server = conn.compute.find_server(name)
        if server:
            server = conn.compute.get_server(server)
            if server.status == "SHUTOFF":
                conn.compute.start_server(server)
                print("%s server has been started" % name)
            else:
                print("%s server is already running" % name)
        else:
            print("Error! %s server was not found" % name)

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    for name in serverNames:
        server = conn.compute.find_server(name)
        if server:
            server = conn.compute.get_server(server)
            if server.status == "ACTIVE":
                conn.compute.stop_server(server)
                print("%s server has been stopped" % name)
            else:
                print("%s server is already stopped" % name)
        else:
            print("Error! %s server was not found" % name)

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    network = conn.network.find_network(NETWORK)
    router = conn.network.find_router(ROUTER)
    #Delete servers
    for name in serverNames:
        server = conn.compute.find_server(name)
        if server:
            conn.compute.delete_server(server)
            print("%s server deleting..." % name)
    print("Waiting for servers to finish deleting...")
    time.sleep(10)
    #Delete Floating IP
    while conn.network.find_available_ip() is not None:
        conn.network.delete_ip(conn.network.find_available_ip())
    #Delete router
    if router:
        conn.network.remove_interface_from_router(router, network.subnet_ids[0])
        conn.network.delete_router(router.id)
        print("Router deleted")
    #Delete network
    if network:
        conn.network.delete_network(network)
        print("Network deleted")

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    for name in serverNames:
        server = conn.compute.find_server(name)
        if server:
            server = conn.compute.get_server(server)
            ip_address = server.addresses[NETWORK][0]["addr"]
            if ip_address is None:
                ip_address = "No address"
            print("%s server:" % name)
            print("Status: %s" % server.status)
            print("Ip Address: %s" % ip_address)
        else:
            print("Error! %s server was not found" % name)


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
