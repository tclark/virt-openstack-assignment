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
    public_net = conn.network.find_network(PUBLIC_NET)
    
    #  Create Network
    network = conn.network.find_network(NETWORK)
    if not network:
        print("Creating network:", str(NETWORK))
        network = conn.network.create_network(name=NETWORK)
    else:
        print("Network already exists:", str(network.name))
    
    #  Create Subnet
    subnet = conn.network.find_subnet(SUBNET)
    if not subnet:
        print("Creating subnet:", str(SUBNET))
        subnet = conn.network.create_subnet(
            name=SUBNET,
            network_id=network.id,
            ip_version=4,
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1')
    else:
        print("Subnet already exists:", str(subnet.name))
    
    #  Create Router
    router = conn.network.find_router(ROUTER)
    if not router:
        print("Creating router:", str(ROUTER))
        router = conn.network.create_router(
            name=ROUTER,
            external_gateway_info={"network_id": public_net.id})
        print("Adding interface to router...")
        conn.network.add_interface_to_router(router, subnet.id)
    else:
        print("Router already exists:", str(router.name))
    
    #  Create floating IP address
    print("Creating floating IP...")
    floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
    
    #  Create Servers
    print("------------------------------")
    web_server = conn.compute.find_server(WEB_SERVER)
    if not web_server:
        print("Creating server:", str(WEB_SERVER))
        web_server = conn.compute.create_server(
            name=WEB_SERVER,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network.id}],
            key_name=keypair.name,
            security_groups=[security_group])
        web_server = conn.compute.wait_for_server(web_server)
        #  Assign floating IP to web server
        print("Assigning floating IP to web server...")
        conn.compute.add_floating_ip_to_server(web_server, floating_ip.floating_ip_address)
    else:
        print("Server already exists:", str(web_server.name))
    
    print("------------------------------")
    app_server = conn.compute.find_server(APP_SERVER)
    if not app_server:
        print("Creating server:", str(APP_SERVER))
        app_server = conn.compute.create_server(
            name=APP_SERVER,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network.id}],
            key_name=keypair.name,
            security_groups=[security_group])
        app_server = conn.compute.wait_for_server(app_server)
    else:
        print("Server already exists:", str(app_server.name))
    
    print("------------------------------")
    db_server = conn.compute.find_server(DB_SERVER)
    if not db_server:
        print("Creating server:", str(DB_SERVER))
        db_server = conn.compute.create_server(
            name=DB_SERVER,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network.id}],
            key_name=keypair.name,
            security_groups=[security_group])
        db_server = conn.compute.wait_for_server(db_server)
    else:
        print("Server already exists:", str(db_server.name))
    
    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    web_server = conn.compute.find_server(WEB_SERVER)
    app_server = conn.compute.find_server(APP_SERVER)
    db_server = conn.compute.find_server(DB_SERVER)
    
    print("------------------------------")
    if web_server:
        web_server = conn.compute.get_server(web_server.id)
        print(str(web_server.name))
        print("Current status:", str(web_server.status))
        if web_server.status == 'SHUTOFF':
            print("Starting web server...")
            conn.compute.start_server(web_server.id)
        else:
            print("Server already running:", str(web_server.name))
    else:
        print("No server named:", str(WEB_SERVER))
    
    print("------------------------------")
    if app_server:
        app_server = conn.compute.get_server(app_server.id)
        print(str(app_server.name))
        print("Current status:", str(app_server.status))
        if app_server.status == 'SHUTOFF':
            print("Starting app server...")
            conn.compute.start_server(app_server.id)
        else:
            print("Server already running:", str(app_server.name))
    else:
        print("No server named:", str(APP_SERVER))
    
    print("------------------------------")
    if db_server:
        db_server = conn.compute.get_server(db_server.id)
        print(str(db_server.name))
        print("Current status:", str(db_server.status))
        if db_server.status == 'SHUTOFF':
            print("Starting db server...")
            conn.compute.start_server(db_server.id)
        else:
            print("Server already running:", str(db_server.name))
    else:
        print("No server named:", str(DB_SERVER))
    
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    web_server = conn.compute.find_server(WEB_SERVER)
    app_server = conn.compute.find_server(APP_SERVER)
    db_server = conn.compute.find_server(DB_SERVER)
    
    print("------------------------------")
    if web_server:
        web_server = conn.compute.get_server(web_server.id)
        print(str(web_server.name))
        print("Current status:", str(web_server.status))
        if web_server.status == 'ACTIVE':
            print("Stopping web server...")
            conn.compute.stop_server(web_server.id)
        else:
            print("Server already stopped:", str(web_server.name))
    else:
        print("No server named:", str(WEB_SERVER))
    
    print("------------------------------")
    if app_server:
        app_server = conn.compute.get_server(app_server.id)
        print(str(app_server.name))
        print("Current status:", str(app_server.status))
        if app_server.status == 'ACTIVE':
            print("Stopping app server...")
            conn.compute.stop_server(app_server.id)
        else:
            print("Server already stopped:", str(app_server.name))
    else:
        print("No server named:", str(APP_SERVER))
    
    print("------------------------------")
    if db_server:
        db_server = conn.compute.get_server(db_server.id)
        print(str(db_server.name))
        print("Current status:", str(db_server.status))
        if db_server.status == 'ACTIVE':
            print("Stopping db server...")
            conn.compute.stop_server(db_server.id)
        else:
            print("Server already stopped:", str(db_server.name))
    else:
        print("No server named:", str(DB_SERVER))
    
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
    
    #  Delete Server
    if web_server:
        print("Deleting server:", str(web_server.name))
        conn.compute.delete_server(web_server)
    else:
        print("No server named:", str(WEB_SERVER))
    if app_server:
        print("Deleting server:", str(app_server.name))
        conn.compute.delete_server(app_server)
    else:
        print("No server named:", str(APP_SERVER))
    if db_server:
        print("Deleting server:", str(db_server.name))
        conn.compute.delete_server(db_server)
    else:
        print("No server named:", str(DB_SERVER))
    
    #  Delete Floating IP
    query = {'status': 'DOWN'}
    floating_ips = conn.network.ips(**query)
    if floating_ips:
        for ip in floating_ips:
            conn.network.delete_ip(ip)
    
    #  Delete Router
    if subnet:
        if router:
            print("Removing interface from router:", str(subnet.name))
            try:
                conn.network.remove_interface_from_router(router.id, subnet.id)
            except Exception as e:
                print("Error removing interface:", str(e))
                pass
            else:
                print("Successfully removed interface!")
        for port in conn.network.get_subnet_ports(subnet.id):
            try:
                print("Deleting port:", str(port.id))
                conn.network.remove_interface_from_router(router, port.id)
                #conn.network.remove_ip_from_port('192.168.50.1')
                conn.network.delete_port(port)
            except Exception as e:
                print("The following error occured when deleting port:", str(e))
    
    if router:
        print("Deleting router:", str(router.name))
        try:
            conn.network.delete_router(router)
        except Exception as e:
            print("The following error occured when deleting router:", str(e))
        else:
            print("Router successfully deleted!")
    else:
        print("No router named:", str(ROUTER))
    
    #  Delete Network and Subnet
    if network:
        print("Deleting subnet:", str(subnet.name))
        for subnet in network.subnet_ids:
            conn.network.delete_subnet(subnet)
        print("Deleting network:", str(network.name))
        conn.network.delete_network(network)
    else:
        print("No network named:", str(NETWORK))
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    web_server = conn.compute.find_server(WEB_SERVER)
    app_server = conn.compute.find_server(APP_SERVER)
    db_server = conn.compute.find_server(DB_SERVER)
    
    print("------------------------------")
    if web_server:
        web_server = conn.compute.get_server(web_server.id)
        print(web_server.name)
        web_status = web_server.status
        print("Status:", str(web_status))
        web_addresses = conn.compute.server_ips(web_server.id)
        print("Addresses:")
        for address in web_addresses:
            print(str(address.network_label), str(address.address))
    else:
        print(str(WEB_SERVER), "does not exist!")
    
    print("------------------------------")
    if app_server:
        app_server = conn.compute.get_server(app_server.id)
        print(app_server.name)
        app_status = app_server.status
        print("Status:", str(app_status))
        app_addresses = conn.compute.server_ips(app_server.id)
        print("Addresses:")
        for address in app_addresses:
            print(str(address.network_label), str(address.address))
    else:
        print(str(APP_SERVER), "does not exist!")
    
    print("------------------------------")
    if db_server:
        db_server = conn.compute.get_server(db_server.id)
        print(db_server.name)
        db_status = db_server.status
        print("Status:", str(db_status))
        db_addresses = conn.compute.server_ips(db_server.id)
        print("Addresses:")
        for address in db_addresses:
            print(str(address.network_label), str(address.address))
    else:
        print(str(DB_SERVER), "does not exist!")
    
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
