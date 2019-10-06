import argparse
import openstack
import time

conn = openstack.connect(cloud_name='openstack', region_name='nz_wlg_2')

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'tiddfc1-net'
KEYPAIR = 'tiddfc1-key'
ROUTER = 'tiddfc1-rtr'
SECURITY_GROUP = 'assignment2'
SERVER_LIST = ['tiddfc1-web', 'tiddfc1-app', 'tiddfc1-db']
SUBNET_IP = '192.168.50.0/24'
SUBNET = 'tiddfc1-subnet'
PUBLICNET = 'public-net'
WEBSERVER = 'tiddfc1-web'

network = conn.network.find_network(NETWORK)
router = conn.network.find_router(ROUTER)
subnet = conn.network.find_subnet(SUBNET)
public_network = conn.network.find_network(PUBLICNET)


def create():
    ''' Create a set of Openstack resources '''
    print('running create function..')
    
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security_group = conn.network.find_security_group(SECURITY_GROUP)
    floating_ip = conn.network.create_ip(floating_network_id=public_network.id)

    if network is None:
        n_network = conn.network.create_network(name=NETWORK, admin_state_up=True)
        print(f'Created Network: {NETWORK}')
    else:
        print(f'Network: {NETWORK} Already Exists')

    if subnet is None:
        n_subnet = conn.network.create_subnet(name=SUBNET, network_id=n_network.id, ip_version='4', cidr=SUBNET_IP)
        print(f'Created Subnet: {SUBNET}')
    else:
        print(f'Subnet: {SUBNET} Already Exists')
    
    if router is None:
        n_router = conn.network.create_router(name=ROUTER, external_gateway_info={'network_id': public_network.id})
        print(f'Created Router: {ROUTER}')
        conn.network.add_interface_to_router(n_router, n_subnet.id)
        print(f'Interface Added To: {ROUTER}')
    else:
        print(f'Router: {ROUTER} Already Exists')

    for servername in SERVER_LIST:
        n_server = conn.compute.find_server(servername)
        if n_server is None:
            print(f'Creating Server: {servername}...')

            server = conn.compute.create_server(
                name=servername, image_id=image.id, flavor_id=flavour.id,
                networks=[{'uuid': n_network.id}], key_name=keypair.name,
                security_groups=[{'name': security_group.name}])

            if servername == 'tiddfc1-web':
                conn.compute.wait_for_server(server)
                conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)
                print(f'Floating Address: {floating_ip.floating_ip_address} Added To {servername}')


        else:
            print(f'Server {server} Already Exists')

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    print('running stop function..')

    for servername in SERVER_LIST:
         c_server = conn.compute.find_server(servername)
         if c_server is not None:
             c_server = conn.compute.get_server(c_server)
             if c_server.status == 'ACTIVE':
                print("1")


def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    print('running destroy function..')


    for servers in SERVER_LIST:
        server = conn.compute.find_server(servers)
        if server is not None:
            conn.compute.delete_server(server)
            print(f'{servers} Being Deleted, This Can Take A Few Seconds..')
            time.sleep(3)
        else:
            print(f'{servers} Already Deleted.')
    
    if router is not None:
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(router)
        print(f'Router: {ROUTER} Deleted')
    else:
        print(f'Router: {ROUTER} Already Deleted')

    if subnet is not None:
        conn.network.delete_subnet(subnet)
        print(f'Subnet: {SUBNET} Deleted')
    else:
        print(f'Subnet: {SUBNET} Already Deleted')

    if network is not None:
        conn.network.delete_network(network)
        print(f'Network: {NETWORK} Deleted')
    else:
        print(f'Network: {NETWORK} Already Deleted')


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
