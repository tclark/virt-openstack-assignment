
  
import argparse
import openstack

IMAGE = 'ubuntu-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
KEYPAIR = 'mariadb'
NETWORK = 'gorda5-net'
SUBNET = 'gorda5-sub'
ROUTER = 'gorda5-rtr'
IP_VERSION = 4
CIDR = '192.168.50.0/24'
SECURITY_GROUP = 'default'
SERVERNAMES = ['gorda5-web', 'gorda5-app', 'gorda5-db']

conn = openstack.connect(cloud_name='openstack')

net = conn.network.find_network(NETWORK)
rtr = conn.network.find_router(ROUTER)
sub = conn.network.find_subnet(SUBNET)
public_net = conn.network.find_network('public-net')

def create():
    ''' Create a set of Openstack resources '''
    image = conn.compute.find_image(IMAGE)
    flavor = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security_group = conn.network.find_security_group(SECURITY_GROUP)

    if not net:
        net_new = conn.network.create_network(name=NETWORK)
        sub_new = conn.network.create_subnet(name=SUBNET, cidr=CIDR, network_id=net_new.id, ip_version=IP_VERSION)
    else:
        print(f'Network {NETWORK} already exists')

    if not rtr:
        rtr_new = conn.network.create_router(name=ROUTER, external_gateway_info={'network_id': public_net.id})
        conn.network.add_interface_to_router(rtr_new, sub_new.id)
    else:
        print(f'Router {ROUTER} already exists')

    for servername in SERVERNAMES:
        if not conn.compute.find_server(servername):
            server = conn.compute.create_server(
                name=servername,
                image_id=image.id, 
                flavor_id=flavor.id, 
                networks=[{'uuid':net_new.id}], 
                key_name=keypair.name, 
                security_groups=[{'sgid':security_group.id}]
            )
            if servername == 'gorda5-web':
                conn.compute.wait_for_server(server)
                fip = conn.network.create_ip(floating_network_id=public_net.id)
                conn.compute.add_floating_ip_to_server(server, fip.floating_ip_address)
                print(f"Web server ip address is: {fip.floating_ip_address}")
        else:
            print(f"Server {servername} already exists")

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    for servername in SERVERNAMES:
       server = conn.compute.find_server(servername)
       if server:
           server = conn.compute.get_server(server)
           if server.status != 'ACTIVE':
               conn.compute.start_server(server)
           

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    for servername in SERVERNAMES:
        server = conn.compute.find_server(servername)
        if server:
            server = conn.compute.get_server(server)
            if server.status == 'ACTIVE':
                conn.compute.stop_server(server)

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    for servername in SERVERNAMES:
        server = conn.compute.find_server(servername)
        if server:
            conn.compute.delete_server(server)
    
    if rtr:
        instances = 3
        while instances > 0:
            instances = 0
            for servername in SERVERNAMES:
                s = conn.compute.find_server(servername)
                if s:
                    instances += 1
        conn.network.remove_interface_from_router(rtr, sub.id)
        conn.network.delete_router(rtr)
    
    if net:
        conn.network.delete_network(net)



def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    for servername in SERVERNAMES:
        server = conn.compute.find_server(servername)
        if server:
            server = conn.compute.get_server(server)
            addresses = []
            for addr in server.addresses[NETWORK]:
                addresses.append(addr['addr'])
            print(f"Server: {server.name}, Status: {server.status}, Addresses: {addresses}")


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