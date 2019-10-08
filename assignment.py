import argparse
import openstack
import time #Importing in-built time module used in my destroy function.

conn = openstack.connect(cloud_name='openstack', region_name='nz_wlg_2') #Creating my connection object to openstack, included my region.

#Defining all my constants.
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'tiddfc1-net'
KEYPAIR = 'tiddfc1-key'
ROUTER = 'tiddfc1-rtr'
SECURITY_GROUP = 'assignment2'
SERVER_LIST = ['tiddfc1-web', 'tiddfc1-app', 'tiddfc1-db'] #Array of server names.
SUBNET_IP = '192.168.50.0/24'
SUBNET = 'tiddfc1-subnet'
PUBLICNET = 'public-net'
WEBSERVER = 'tiddfc1-web'

#Searching for existing network objects by passing in my constants.
network = conn.network.find_network(NETWORK)
router = conn.network.find_router(ROUTER)
subnet = conn.network.find_subnet(SUBNET)
public_network = conn.network.find_network(PUBLICNET)


def create():
    ''' Create a set of Openstack resources '''
    print('running create function..')
   
   # Note order of the creation of openstack objects is important, example network then subnet etc..

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security_group = conn.network.find_security_group(SECURITY_GROUP)
    floating_ip = conn.network.create_ip(floating_network_id=public_network.id)

    if network is None: #If network is null.
        n_network = conn.network.create_network(name=NETWORK, admin_state_up=True) #Creating network.
        print(f'Created Network: {NETWORK}')
    else:
        print(f'Network: {NETWORK} Already Exists')

    if subnet is None: #If subnet search returns null.
        n_subnet = conn.network.create_subnet(name=SUBNET, network_id=n_network.id, ip_version='4', cidr=SUBNET_IP) #Creating and adding subnet to network.
        print(f'Created Subnet: {SUBNET}')
    else:
        print(f'Subnet: {SUBNET} Already Exists')
    
    if router is None: #If router is null.
        n_router = conn.network.create_router(name=ROUTER, external_gateway_info={'network_id': public_network.id}) #Creating router with constants.
        print(f'Created Router: {ROUTER}')
        conn.network.add_interface_to_router(n_router, n_subnet.id) # Assigning router to network.
        print(f'Interface Added To: {ROUTER}')
    else:
        print(f'Router: {ROUTER} Already Exists')

    for servername in SERVER_LIST: # Running for loop through servername array.
        n_server = conn.compute.find_server(servername) # Checking if server already exists.
        if n_server is None: # If server doesnt exist.
            print(f'Creating Server: {servername}...')

            server = conn.compute.create_server(
                name=servername, image_id=image.id, flavor_id=flavour.id,
                networks=[{'uuid': n_network.id}], key_name=keypair.name,
                security_groups=[{'name': security_group.name}]) # Creating server instance, passing all constants defined above.

            if servername == 'tiddfc1-web': # Assigning floating ip to web server.
                conn.compute.wait_for_server(server) #Waiting for server to finish creation.
                conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address) #Adding floating ip.
                print(f'Floating Address: {floating_ip.floating_ip_address} Added To {servername}')


        else:
            print(f'Server {server} Already Exists')

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    print('running run fucntion')

    for servername in SERVER_LIST: # Running for loop through serername arrary.
        c_server = conn.compute.find_server(servername) # Set server found set it as current server.
        if c_server is not None: # If current server is not null.
            c_server = conn.compute.get_server(c_server) # Pull infomation from current server ie Status etc.
            if c_server.status == 'SHUTOFF': # If server is in shutdown mode enter if statement.
                print(f'{servername} Booting up..')
                conn.compute.start_server(c_server) # Boot up server.
            elif c_server.status == 'ACTIVE': # If server is currently active. 
                 print(f'{servername} Is Already Running..') # Log out to user.
        else:
            print(f'Error: {servername} Does Not Exist..') # If server is not found, log out error message.

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    print('running stop function..')

    for servername in SERVER_LIST: # Running for loop through servername array.
        c_server = conn.compute.find_server(servername) # Set server found set as current server.
        if c_server is not None: # If current server is not null.
            c_server = conn.compute.get_server(c_server) # Pull server information.
            if c_server.status == 'ACTIVE': # If status of server is Active/Live enter if.
               print(f'{servername} is Active, Shuting Down..')
               conn.compute.stop_server(c_server) # Shutdown server.
            elif c_server.status == 'SHUTOFF':
                 print(f'{servername} Shutdown Already..') # Log out status to user.
        else:
            print(f'Error: {servername} Does Not Exist..') # If server doesnt exist log out error message.


def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    print('running destroy function..')

    # Note order of deletion of objects is important.

    for servers in SERVER_LIST: # Running for loop through sernames array.
        server = conn.compute.find_server(servers) 
        if server is not None: # If current server is not null.
            conn.compute.delete_server(server) # Delete current server in loop.
            print(f'{servers} Being Deleted, This Can Take A Few Seconds..') # Log action to user.
            time.sleep(3) # Used a .sleep here due to script moving to fast not allowing server to delete in time. conn.wait_for_server did not work. Used sleep instead.
        else:
            print(f'{servers} Already Deleted.') # If null log server doesn't exist/deleted.
    
    if router is not None: # If router exists enter if.
        conn.network.remove_interface_from_router(router, subnet.id) # First remove interface from router.
        conn.network.delete_router(router) # Delete router itself.
        print(f'Router: {ROUTER} Deleted')
    else:
        print(f'Router: {ROUTER} Already Deleted') # Log to user.

    if subnet is not None: # If subnet exists enter if.
        conn.network.delete_subnet(subnet) # Delete subnet.
        print(f'Subnet: {SUBNET} Deleted')
    else:
        print(f'Subnet: {SUBNET} Already Deleted')

    if network is not None: # If network exists enter if.
        conn.network.delete_network(network) # Delete network.
        print(f'Network: {NETWORK} Deleted') # Log out to user.
    else:
        print(f'Network: {NETWORK} Already Deleted')


def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    print('running status function..')
    
    for servername in SERVER_LIST: # Running for loop through servername list.
        c_server = conn.compute.find_server(servername) # Find and set current server.
        if c_server is not None: # If current server exists.
            c_server = conn.compute.get_server(c_server) # Get current server information.
            for info in c_server.addresses[NETWORK]: # c.server.addresses returns a large array of information on the server, run loop to filter through for each server.
                print(f'Server: {servername} // Status: {c_server.status} // Addresses: ' + info['addr'] + ' // Type: ' + info['OS-EXT-IPS:type']) # Pull out addr which is address and OS-EXT-IPS:type which is the type of IP.
                ## print(f'{c_server.addresses}')
        else:
            print(f'Error: {servername} Does Not Exist..') # Log non existing error out to user.


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
