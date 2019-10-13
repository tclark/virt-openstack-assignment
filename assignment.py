import argparse
import openstack

def create():

    ''' Create a set of Openstack resources '''

    '''create variables'''
    IMAGE = 'ubuntu-16.04-x86_64'
    FLAVOR = 'c1.c1r1'
    NETWORK = 'hachm1-net'
    KEYPAIR = 'hachm1-key'

    image = conn.compute.find_image(IMAGE)
    flavor = conn.compute.find_flavor (FLAVOR)
    network = conn.network.find_network(NETWORK)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security_group = conn.network.find_security_group('assignment2')

    
    '''create a network'''
    network = conn.network.find_network('hachm1-net')
    if network is not None:
        hachm1_net = conn.network.create_network(name = 'hachm1-net')

        '''create subnet'''
        hachm1_subnet = conn.network.create_subnet(
        name ='hachm1-subnet',
        network_id = network.id,
        ip_version = 4,
        cidr ='192.168.50.0/24',
        gateway_ip = '192.168.50.1/24'
        )
    else:
        print("error")


    
    '''create routers'''

    router = conn.network.find_router('hachm1-rtr')
    if router is not None:
        public_net = conn.network.find_network('public-net')
        hachm1-rtr = conn.network.create_router(name='hachm1-rtr', external_gateway_info={'network_id':public_net.id})
        conn.network.add_interface_to_router(hachm1-rtr, hachm1_subnet.id)

    else:
        print("error")

    '''create servers
    if exits do not create again
    '''

    server = conn.compute.find_server('hachm1-web')
    if server is not None:
        SERVER = 'hachm1-web'
        server.conn.compute.create_server(
            name = SERVER, image_id =image.id, flavor = flavor.id,
            networks = [{"uuid":hachm1_net.id}], key_name = keypair.name,
            security_group=[{'name:'security_group.id}]
        )
        server = conn.compute.wait_for_server(server)

    server = conn.compute.find_server('hachm1-app')
    if server is not None:
        SERVER = 'hachm1-app'
        server.conn.compute.create_server(
            name = SERVER, image_id - image.id, flavor = flavor.id,
            networks = [{"uuid":hachm1_net.id}], key_name = keypair.name
            security_group=[{'name:'security_group.id}]
        )
        server = conn.compute.wait_for_server(server)

    server = conn.compute.find_server('hachm1-db')
    if server is not None:
        SERVER = 'hachm1-db'
        server.conn.compute.create_server(
            name = SERVER, image_id - image.id, flavor = flavor.id,
            networks = [{"uuid":hachm1_net.id}], key_name = keypair.name
            security_group=[{'name:'security_group.id}]
        )
        server = conn.compute.wait_for_server(server)


    '''associate a floating IP address'''
    web-server = conn.compute.find_server('hachm1-web')
    if web-server is not None:
        floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
        conn.compute.add_floating_ip_to_server('hachm1-web',floating_ip.floating_ip_address)

    pass

def run():

    ''' Start  a set of Openstack virtual machines
    if they are not already running
    '''


    server = conn.compute.find_server('hachm1-web')
    if server is not None:
        server = conn.compute.get_server('hachm1-web')
        if server.status = 'ACTIVE':
            print ('server is running')

        elif server.status='SHUTOFF':
            conn.compute.start_server('hachm1-web')
    
    server = conn.compute.find_server('hachm1-app')
    if server is not None:
        server = conn.compute.get_server('hachm1-app')
        if server.status = 'ACTIVE':
            print ('server is running')

        elif server.status='SHUTOFF':
            conn.compute.start_server('hachm1-app')
    
    server = conn.compute.find_server('hachm1-db')
    if server is not None:
        server = conn.compute.get_server('hachm1-db')
        if server.status = 'ACTIVE':
            print ('server is running')

        elif server.status='SHUTOFF':
            conn.compute.start_server('hachm1-db')
    

    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''

    server = conn.compute.find_server('hachm1-web')
    if server is not None:
        server = conn.compute.get_server('hachm1-web')
        if server.status = 'ACTIVE':
            conn.compute.stop_server('hachm1-web')

        elif server.status='SHUTOFF':
            print('server is not running')
    
    server = conn.compute.find_server('hachm1-app')
    if server is not None:
        server = conn.compute.get_server('hachm1-app')
        if server.status = 'ACTIVE':
            conn.compute.stop_server('hachm1-app')

        elif server.status='SHUTOFF':
            print('server is not running')
    
    server = conn.compute.find_server('hachm1-db')
    if server is not None:
        server = conn.compute.get_server('hachm1-db')
        if server.status = 'ACTIVE':
            conn.compute.stop_server('hachm1-db')

        elif server.status='SHUTOFF':
            print('server is not running')
    
    pass

def destroy():
    ''' Tear down the set of Openstack resources
    produced by the create action
    '''

    '''delete servers'''
    print ("delete server")
    server = conn.compute.find_server('hachm1-web')
    if server is not None:
        conn.delete_server(server)
    
    server = conn.compute.find_server('hachm1-app')
    if server is not None:
        conn.delete_server(server)

    server = conn.compute.find_server('hachm1-db')
    if server is not None:
        conn.delete_server(server)

    '''delete network'''
    print ("delete network")

    sub = conn.network.find_subnet('hachm1-subnet')
    router = conn.network.find_router('hachm1-rtr')
    conn.network.remove_interface_from_router(router, sub.id)
    conn.network.delete_router(router)
    print ('router destroyed')

    subnet = conn.network.find_subnet('hachm1-sub')
    conn.network.delete_subnet(subnet)
    print ('subnet destroyed')


    network = conn.network.find_network('hachm1-net')
    conn.network.delete_network(network)
    print ('network destroyed')

    pass

def status():
    '''Print a status report on the OpenStack
    virtual machines created by the create action.
    '''


    hachm1-web = conn.compute.find_server('hachm1-web')
    if hachm1-web is not None:
        server = conn.compute.get_server(hachm1-web)
        print ({server.name, server.status, server.addresses})

    hachm1-app = conn.compute.find_server('hachm1-app')
    if hachm1-app is not None:
        server = conn.compute.get_server(hachm1-app)
        print ({server.name, server.status, server.addresses}) 

    hachm1-db = conn.compute.find_server('hachm1-db')
    if hachm1-db is not None:
        server = conn.compute.get_server(hachm1-db)
        print ({server.name, server.status, server.addresses})
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
