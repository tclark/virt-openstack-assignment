import argparse
import openstack

CLOUD = 'otago-polytechnic'
REGION = 'nz-hlz-1'
NETWORK = 'cougcj1-net'
SUBNET = 'cougcj1-subnet'
SUBNET_IP = '192.168.50.0/24'
GATEWAY = '192.168.50.1'
ROUTER = 'cougcj1-rtr'
PUBLIC_NET = 'public-net'
WEB_SERVER = 'cougcj1-web'
APP_SERVER = 'cougcj1-app'
DB_SERVER = 'cougcj1-db'
IMAGE_NAME = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR_NAME = 'c1.c1r1'
SEC_GROUP = 'assignment2'
KEY_PAIR = 'cougcj1-key'

def set_up_connection():
    # Requires cloud file in same directory
    print('Connecting to cloud.')
    conn = openstack.connect(cloud_name = CLOUD, region_name = REGION)
    if conn is None:
        print('Error connecting to network. Check you have included a "clouds.yaml" file in the local directory.')
        exit()

    return conn

def create():
    # Set up a connection to the openstack network
    print('Setting up connection.')
    conn = set_up_connection()

    # Checks for existing network
    # If none, we create one
    print('Checking to see if network exists.')
    network = conn.network.find_network(NETWORK)
    if network is None:
        print('Creating network.')
        network = conn.network.create_network(name = NETWORK)

    # Checks for and creates subnet
    print('Checking to see if subnet exists.')
    subnet = conn.network.find_subnet(SUBNET)
    if subnet is None:
        print('Creating subnet.')
        subnet = conn.network.create_subnet(
            name = SUBNET,
            network_id = network.id,
            ip_version = '4',
            cidr = SUBNET_IP,
            gateway_ip = GATEWAY)

    # Checks for and creates router, interfacing with the newly created and public networks
    print('Checking to see if router exits.')
    router = conn.network.find_router(ROUTER)
    if router is None:
        print('Creating router.')
        public_net = conn.network.find_network(PUBLIC_NET)
        router_config = {
                'name': ROUTER,
                'external_gateway_info': {'network_id' : public_net.id}
                }
        router = conn.network.create_router(**router_config)

        print('Adding subnet to router.')
        router = conn.network.add_interface_to_router(
            router.id,
            subnet_id = subnet.id)

    # Checks for and creates servers
    image = conn.compute.find_image(IMAGE_NAME)
    flavor = conn.compute.find_flavor(FLAVOUR_NAME)
    network = conn.network.find_network(NETWORK)
    public_net = conn.network.find_network(PUBLIC_NET)
    sec_group = conn.network.find_security_group(name_or_id=SEC_GROUP) 
    keypair = conn.compute.find_keypair(KEY_PAIR)

    print('Checking for existing web server.')
    if conn.compute.find_server(WEB_SERVER) is None:
        print('Setting up web server.')
        web_server = conn.compute.create_server(
            name=WEB_SERVER, image_id=image.id, flavor_id=flavor.id,
            networks=[{'uuid': network.id}], key_name=keypair.name)
        web_server = conn.compute.wait_for_server(web_server)
        conn.add_server_security_groups(web_server, sec_group)
        # Create floating IP address associated with the network created above.
        # If a floating IP is already associated with the network it is returned instead.
        # This address is for the web server
        web_server = conn.compute.find_server(WEB_SERVER)
        floating_IP = conn.create_floating_ip(network=public_net, server=web_server)

    print('Checking for existing app server.')
    if conn.compute.find_server(APP_SERVER) is None:
        print('Setting up app server.')
        app_server = conn.compute.create_server(
            name=APP_SERVER, image_id=image.id, flavor_id=flavor.id,
            networks=[{'uuid': network.id}], key_name=keypair.name)
        app_server = conn.compute.wait_for_server(app_server)
        conn.add_server_security_groups(app_server, sec_group)

    print('Checking for existing db server.')
    if conn.compute.find_server(DB_SERVER) is None:
        print('Setting up db server.')   
        db_server = conn.compute.create_server(
            name=DB_SERVER, image_id=image.id, flavor_id=flavor.id,
            networks=[{'uuid': network.id}], key_name=keypair.name)
        db_server = conn.compute.wait_for_server(db_server)
        conn.add_server_security_groups(db_server, sec_group)

    conn.close()

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    conn = set_up_connection()

    web_server = conn.get_server(WEB_SERVER)
    app_server = conn.get_server(APP_SERVER)
    db_server = conn.get_server(DB_SERVER)
    
    if web_server is None:
        print('Web server does not exist.')
    else:
        if web_server.status != 'ACTIVE':
            conn.compute.start_server(web_server)
            print('Web server status changed to Active.')

    if app_server is None:
        print('App server does not exist.')
    else:
        if app_server.status != 'ACTIVE':
            conn.compute.start_server(app_server)
            print('App server status changed to Active.')
    if db_server is None:
        print('Db server does not exist.')
    else:
        if db_server.status != 'ACTIVE':
            conn.compute.start_server(db_server)
            print('Db server status changed to Active.')

    conn.close()

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    conn = set_up_connection()

    web_server = conn.get_server(WEB_SERVER)
    app_server = conn.get_server(APP_SERVER)
    db_server = conn.get_server(DB_SERVER)

    if web_server is None:
        print('Web server does not exist.')
    else:
        if web_server.status == 'ACTIVE':
            conn.compute.stop_server(web_server)
            print('Web server status changed to Down.')

    if app_server is None:
        print('App server does not exist.')
    else:
        if app_server.status == 'ACTIVE':
            conn.compute.stop_server(app_server)
            print('App server status changed to Down.')
    if db_server is None:
        print('Db server does not exist.')
    else:
        if db_server.status == 'ACTIVE':
            conn.compute.stop_server(db_server)
            print('Db server status changed to Down.')

    conn.close()

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    conn = set_up_connection()

    # Destroy Servers
    web_server = conn.compute.find_server(WEB_SERVER)
    if web_server is not None:
        conn.compute.delete_server(
                web_server.id,
                ignore_missing=True)
    
    app_server = conn.compute.find_server(APP_SERVER)
    if app_server is not None:
        conn.compute.delete_server(
                app_server.id,
                ignore_missing=True)
    
    db_server = conn.compute.find_server(DB_SERVER)
    if db_server is not None:
        conn.compute.delete_server(
                db_server.id,
                ignore_missing=True)

    conn.delete_unattached_floating_ips()

    # Destroy router
    router = conn.network.find_router(ROUTER)
    if router is not None:
        subnet = conn.network.find_subnet(SUBNET)
        if subnet is not None:
            conn.network.remove_interface_from_router(
                router.id,
                subnet_id = subnet.id)
        conn.network.delete_router(router.id)

    # Destroy subnet
    subnet = conn.network.find_subnet(SUBNET)
    if subnet is not None:
        conn.network.delete_subnet(subnet.id)

    # Destroy network
    network = conn.network.find_network(NETWORK)
    if network is not None:
        conn.network.delete_network(network.id)

    conn.close()

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    conn = set_up_connection()

    web_server = conn.get_server(WEB_SERVER)
    app_server = conn.get_server(APP_SERVER)
    db_server = conn.get_server(DB_SERVER)

    if web_server is not None:
        print('Web server status:')
        print(web_server.status)
        if web_server.status == 'ACTIVE':
            for address in conn.compute.server_ips(web_server.id):
                print(address.address)
            print('')
        else:
            print('Web server is currently down.')
    else:
        print('Web server does not exist.')

    if app_server is not None:
        print('App server status:')
        print(app_server.status)
        if app_server.status == 'ACTIVE':
            for address in conn.compute.server_ips(app_server.id):
                print(address.address)
            print('')
        else:
            print('App server is currently down.')
    else:
        print('App server does not exist.')
        
    if db_server is not None:
        print('Db server status:')
        print(db_server.status)
        if db_server.status == 'ACTIVE':
            for address in conn.compute.server_ips(db_server.id):
                print(address.address)
            print('')
        else:
            print('Db server is currently down.')
    else:
        print('Db server does not exist.')

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
