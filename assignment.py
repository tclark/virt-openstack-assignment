import argparse
import openstack

#  Connect to the openstack service
conn = openstack.connect(cloud_name=’openstack’)
#  Creating resource name variables
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
KEYPAIR = 'clarjc3-key'
PUBLIC_NETWORK = 'public-net'
NETWORK = 'clarjc3-net'
SUBNET = 'clarjc3-subnet'
ROUTER = 'clarjc3-rtr'
SECURITY_GROUP='assignment2'

def create():
    ''' Create a set of Openstack resources '''
    #  Get resources from the cloud
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavour(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security_group = conn.network.find_security_group(SECURITY_GROUP)
    
    #  Create Network
    network = conn.network.find_network(NETWORK)
    if not network:
        network = conn.network.create_network(name=NETWORK)
    
    #  Create Subnet
    subnet = conn.network.find_subnet(SUBNET)
    if not subnet:
        subnet = conn.network.create_subnet(
            name=SUBNET,
            network_id=network.id,
            ip_version=4,
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1')
    
    #  Create Router
    public_network = conn.network.find_network(PUBLIC_NETWORK)
    router = conn.network.find_router(ROUTER)
    if not router:
        router = conn.network.create_router(
            name=ROUTER,
            external_gateway_info={"network_id": public_network.id})
        conn.network.router_add_interface(router, subnet.id)
    
    #  Create floating IP address
    floating_ip = conn.network.create_ip(floating_network_id=network.id)
    
    #  Create Server
    SERVER = 'clarjc3-server'
    #clarjc3-web, clarjc3-app, clarjc3-db
    server = conn.compute.find_server(SERVER)
    if not server:
        server = conn.compute.create_server(
            name=SERVER,
            image_id=image.id,
            flavour_id=flavour.id,
            networks=[{"uuid": network.id}],
            key_name=keypair.name)
        server = conn.compute.wait_for_server(server)
        conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address) #  Assign floating IP to web server
    
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
    #  Delete Server
    
    #  Delete Floating IP
    
    #  Delete Router
    router = conn.network.find_router(ROUTER)
    if router:
        conn.network.
        conn.network.delete_router(ROUTER)
    #  Delete Network
    network = conn.network.find_network(NETWORK)
    if network:
        for subnet in network.subnet_ids:
            conn.network.delete_subnet(subnet)
        conn.network.delete_network(network)
    
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
