import argparse
import openstack

#  Connect to the openstack service
conn = openstack.connect(cloud_name='openstack')
#  Creating resource name variables
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOR = 'c1.c1r1'
KEYPAIR = 'clarjc3-key'
PUBLIC_NET = 'public-net'
NETWORK = 'clarjc3-net'
SUBNET = 'clarjc3-subnet'
ROUTER = 'clarjc3-rtr'
SECURITY_GROUP = 'assignment2'
WEB_SERVER = 'clarjc3-web'
APP_SERVER = 'clarjc3-app'
DB_SERVER = 'clarjc3-db'
FLOATING_IP = 'clarjc3-ip'

def create():
    ''' Create a set of Openstack resources '''
    #  Get resources from the cloud
    image = conn.compute.find_image(IMAGE)
    flavor = conn.compute.find_flavor(FLAVOR)
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
    public_net = conn.network.find_network(PUBLIC_NET)
    router = conn.network.find_router(ROUTER)
    if not router:
        router = conn.network.create_router(
            name=ROUTER,
            external_gateway_info={"network_id": public_net.id})
        conn.network.add_interface_to_router(router, subnet.id)
    
    #  Create floating IP address
    floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
    
    #  Create Servers
    web_server = conn.compute.find_server(WEB_SERVER)
    if not web_server:
        web_server = conn.compute.create_server(
            name=WEB_SERVER,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network.id}],
            key_name=keypair.name)
        web_server = conn.compute.wait_for_server(web_server)
        conn.compute.add_floating_ip_to_server(web_server, floating_ip.floating_ip_address) #  Assign floating IP to web server
    app_server = conn.compute.find_server(APP_SERVER)
    if not app_server:
        app_server = conn.compute.create_server(
            name=APP_SERVER,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network.id}],
            key_name=keypair.name)
        app_server = conn.compute.wait_for_server(app_server)
    db_server = conn.compute.find_server(DB_SERVER)
    if not db_server:
        db_server = conn.compute.create_server(
            name=DB_SERVER,
            image_id-image.id,
            flavor_id=flavor.id,
            networks[{"uuid": network.id}],
            key_name=keypair.name)
        db_server = conn.compute.wait_for_server(db_server)
    
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
    #  Finding resources
    router = conn.network.find_router(ROUTER)
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet(SUBNET)
    web_server = conn.compute.find_server(WEB_SERVER)
    app_server = conn.compute.find_server(APP_SERVER)
    db_server = conn.compute.find_server(DB_SERVER)
    #floating_ip = conn.network.find_ip()
    #  Delete Server
    if web_server:
        conn.compute.delete_server(web_server)
    if app_server:
        conn.compute.delete_server(app_server)
    if db_server:
        conn.compute.delete_server(db_server)
    #  Delete Floating IP
    #if floating_ip:
    #    conn.compute.remove_floating_ip_from_server(server, floating_ip)
    #    conn.network.delete_ip(floating_ip)
    #  Delete Router
    if router:
        try:
            conn.network.remove_interface_from_router(router.id, subnet.id)
        except:
            pass
        for port in conn.network.get_subnet_ports(subnet.id):
            conn.network.delete_port(port)
        conn.network.delete_router(router)
    #  Delete Network and Subnet
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
