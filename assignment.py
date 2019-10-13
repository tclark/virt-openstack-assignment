import argparse
import openstack
import re

CLOUD = 'otago-polytechnic'
REGION = 'nz_wlg_2'
NET = 'bishk3-net'
SUBNET = 'bishk3-subnet'
SUBNET_IP = '192.168.50.0/24'
GATEWAY = '192.168.50.1'
ROUTER = 'bishk3-rtr'
PUBLIC_NET = 'public-net'
SERVER_IMAGE = "ubuntu-minimal-16.04-x86_64"
SERVER_FLAVOR = "c1.c1r1"
SERVER_NAMES = ["bishk3-web", "bishk3-app", "bishk3-db"]
KEYPAIR_NAME = "bishk3-key"
SECURITY_GROUP = "assignment2"
WEB_SERVER = "bishk3-web"
IP_REGEX = re.compile('192\.168\.50\.*')

def set_up_connection():
    ''' Sets up a connection to the openstack network '''
    # This assumes there is a clouds.yaml file in the local direcotry
    print("Connecting to %s" % CLOUD)
    conn = openstack.connect(
        cloud_name = CLOUD,
        region_name = REGION)
    if conn is None:
        print('Error connecting to network.  Please check you have included a "clouds.yaml" file in the local directory and try again.')
        exit()

    return conn

# Thing here refers to the object being passed in
# e.g., router name, network name etc
def creation_error(conn, thing):
    print("Error creating %s." % thing)
    conn.close()
    exit()

def deletion_error(conn, thing):
    print("Error deleting %s." % thing)
    conn.close()
    exit()

def servers_do_not_exist(conn):
    print("Please create servers first then try again.")
    conn.close()
    exit()

def create():
    ''' Create a set of Openstack resources '''
    # First we set up a connection to the openstack network
    print("Setting up connection")
    conn = set_up_connection()

    # Then we create our network
    ## First we check to see if the network already exists
    print("Checking to see if %s exists" % NET)
    network = conn.network.find_network(NET)
    if network is None:
        print("Creating %s" % NET)
        network = conn.network.create_network(
            name = NET)
        if network is None:
            creation_error(conn, NET)
        print("Successfully created %s!" % NET)

    ## Next we create the subnet for a our network that the
    ## hosts will connect to, checking first that it doesn't
    ## already exist
    print("Checking to see if %s exists" % SUBNET)
    subnet = conn.network.find_subnet(SUBNET)
    if subnet is None:
        print("Creating %s" % SUBNET)
        subnet = conn.network.create_subnet(
            name = SUBNET,
            network_id = network.id,
            ip_version = '4',
            cidr = SUBNET_IP,
            gateway_ip = GATEWAY)
        if subnet is None:
            creation_error(conn, SUBNET)
        print("Successfully created %s!" % SUBNET)

    ## Next we create the router, pointing one interface at the 
    ## public network, and another at our newly created network
    print("Checking to see if %s exits" % ROUTER)
    router = conn.network.find_router(ROUTER)
    if router is None:
        print("Creating %s" % ROUTER)
        public_network = conn.network.find_network(PUBLIC_NET)
        ### Create dictonary of values to pass to router object to be used
        ### upon creation
        router_properties = {
            "name": ROUTER,
            "external_gateway_info": {"network_id": public_network.id}
            }
        router = conn.network.create_router(**router_properties)
        if router is None:
            creation_error(conn, ROUTER)

        print("Adding interfaces to router")
        router = conn.network.find_router(ROUTER)
        router = conn.network.add_interface_to_router(
            router.id,
            subnet_id = subnet.id)
        if router is None:
            creation_error(conn, ROUTER)
        print("Successfully created %s!" % ROUTER)

    ## Create the three servers
    for server_name in SERVER_NAMES:
        print("Checking if %s exists" % server_name)
        server = conn.compute.find_server(server_name)
        if server is None:
            image = conn.compute.find_image(SERVER_IMAGE)
            flavor = conn.compute.find_flavor(SERVER_FLAVOR)
            keypair = conn.compute.find_keypair(KEYPAIR_NAME)
            print("Creating %s" % server_name)
            server = conn.compute.create_server(
                name = server_name,
                image_id = image.id,
                flavor_id = flavor.id,
                networks = [{"uuid": network.id}],
                key_name = keypair.name)
            server = conn.compute.wait_for_server(server)
            if server is None:
                creation_error(conn, server_name)
            
            print("Assigning %s to security group %s" % (server_name, SECURITY_GROUP))
            security_group = conn.network.find_security_group(SECURITY_GROUP)
            conn.compute.add_security_group_to_server(
                server.id, 
                security_group)
            
            if server_name is WEB_SERVER:
                print("Assigning floating IP to %s" % server_name)
                ip_parameters = {
                    "floating_network_id": public_network.id}
                floating_ip = conn.network.create_ip(**ip_parameters)
                conn.compute.add_floating_ip_to_server(
                    server.id,
                    floating_ip.floating_ip_address)
            print("Servers successfully created!")

    conn.close()

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    print("Setting up connection to cloud")
    conn = set_up_connection()

    for server_name in SERVER_NAMES:
        ## We have to first find the server as the find server returns
        ## A server detail not an actual server instance and so is 
        ## unable to return any values related to the running of the
        ## server.  Once we have to detail we can call get_server which
        ## returns a full server instance containing all the details we
        ## need
        server_details = conn.compute.find_server(server_name)
        if server_details is None:
            servers_do_not_exist(conn)
  
        server = conn.compute.get_server(server_details.id)
        if server.status == 'SHUTOFF':
            print("Starting %s" % server_name)
            conn.compute.start_server(server.id)

    conn.close()

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    print("Setting up connection to cloud")
    conn = set_up_connection()

    for server_name in SERVER_NAMES:
        ## We have to first find the server as the find server returns
        ## A server detail not an actual server instance and so is 
        ## unable to return any values related to the running of the
        ## server.  Once we have to detail we can call get_server which
        ## returns a full server instance containing all the details we
        ## need
        server_details = conn.compute.find_server(server_name)
        if server_details is None:
            servers_do_not_exist(conn)

        server = conn.compute.get_server(server_details.id)
        if server.status == 'ACTIVE':
            print("Stopping %s" % server_name)
            conn.compute.stop_server(server.id)

    conn.close()

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    # Set up connection to network
    print('Setting up connection')
    conn = set_up_connection()  

    # Destroy servers
    for server_name in SERVER_NAMES:
        print("Finding %s" % server_name)
        server = conn.compute.find_server(server_name)
        if server is not None:
            if server_name is WEB_SERVER:
                print("Removing Floating IP from %s" % server_name)
                server_ips = conn.compute.server_ips(server.id)
                for ip in server_ips:
                    if not re.match(IP_REGEX, ip.address):
                        floating_ip_address = ip
                floating_ip = conn.network.find_ip(floating_ip_address.address)
                conn.network.delete_ip(floating_ip.id)

            print("Destroying %s" % server_name)
            conn.compute.delete_server(
                server.id,
                ignore_missing = True)
    
    # Destroy router
    print("Finding %s" % ROUTER)
    router = conn.network.find_router(ROUTER)
    if router is not None:
        print("Removing active interfaces from %s" % ROUTER)            
        subnet = conn.network.find_subnet(SUBNET)                  
        if subnet is not None:
            destruction_status = conn.network.remove_interface_from_router(
                router.id,
                subnet_id = subnet.id)
            if destruction_status is False:
                deletion_error(conn, ROUTER)

        print("Destroying %s" % ROUTER)     
        conn.network.delete_router(router.id)
        print("Successfully deleted %s!" % ROUTER)

    # Destroy subnet
    print("Finding %s" % SUBNET)
    subnet = conn.network.find_subnet(SUBNET)
    if subnet is not None:
        print("Destroying %s" % SUBNET)
        conn.network.delete_subnet(subnet.id)
        print("Successfully deleted %s!" % SUBNET)

    # Destroy network
    print("Finding network %s" % NET)
    network = conn.network.find_network(NET)
    if network is not None:
        print("Destroying %s" % NET)
        conn.network.delete_network(network.id)
        print("Successfully deleted %s!" % NET)
    
    conn.close()

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    # Set up connection to network
    print('Setting up connection')
    conn = set_up_connection()  

    for server_name in SERVER_NAMES:
        server_details = conn.compute.find_server(server_name)
        if server_details is not None:
            server = conn.compute.get_server(server_details.id)
            print("SERVER: %s" % server_name)
            print("STATUS: %s" % server.status)
            if server.status == 'ACTIVE':
                server_ips = conn.compute.server_ips(server.id)
                for server_ip in server_ips:
                    print("IP ADDRESS: %s" % server_ip.address)
            print("===")

    conn.close()

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
