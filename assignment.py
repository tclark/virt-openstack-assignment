import argparse
import openstack

NETWORK = 'wangh21-net'
SUBNET = 'wangh21-subnet'
CIDR = '192.168.50.0/24'
ROUTER = 'wangh21-rtr'
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
SERVERLIST = ['wangh21-web', 'wangh21-app', 'wangh21-db']
SECURITYGROUP = 'assignment2'
KEYPAIRNAME = 'hua'

conn = openstack.connect(cloud_name='openstack')


def check_parameter():
    # declare variable ref from:  https://github.com/openstack/openstacksdk/blob/master/examples/compute/create.py
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIRNAME)
    security_group = conn.network.find_security_group(SECURITYGROUP)
    public_net = conn.network.find_network('public-net')

    # check network subnet router whether exists to avoid recreate
    network = conn.network.find_network(NETWORK)
    if(network == None):
        network = conn.network.create_network(name=NETWORK)

    subnet = conn.network.find_subnet(SUBNET)
    if(subnet == None):
        subnet = conn.network.create_subnet(
            name=SUBNET, network_id=network.id, ip_version=4, cidr=CIDR)

    router = conn.network.find_router(ROUTER)
    if (router == None):
        router = conn.network.create_router(name=ROUTER,
                                            external_gateway_info={'network_id': public_net.id})
        router = conn.network.add_interface_to_router(router, subnet.id)

def create():
    ''' Create a set of Openstack resources '''

    print('Preparing to create resources, please wait...')
    check_parameter()

    # start create server from SERVERLIST
    for server in SERVERLIST:
        s = conn.compute.find_server(server)
        if(s == None):
            print(f"Create Server {server}...")
            s = conn.compute.create_server(
                name=server,
                image_id=image.id,
                flavor_id=flavour.id,
                networks=[{'uuid': network.id}],
                key_name=keypair.name,
                security_groups=[{'sgid': security_group.id}]
            )
        else:
            print(f'The server {server} has already exists...')

        # add floating ip for wangh21-web server
        if(server == SERVERLIST[0]):
            conn.compute.wait_for_server(s)
            # if the web server only already have one ip
            if(len(conn.compute.get_server(s.id)['addresses']['wangh21-net']) < 2):
                floating_ip = conn.network.create_ip(
                    floating_network_id=public_net.id).floating_ip_address
                conn.compute.add_floating_ip_to_server(s, floating_ip)
                print(f'Floating IP {floating_ip} added to {server}.')
    print('Operation completed.')
    pass


def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    print(f'Current status:')
    status()

    for server in SERVERLIST:
        s = conn.compute.find_server(server)  # get server
        ss = conn.compute.get_server(
            conn.compute.find_server(server).id)  # get status
        # 1. create server when server does not exists 2. check the server whehter running 3. start server
        if(s == None):
            print(
                f'The Server {server} has not created. Please run this script with create parameter first.')
        elif(ss.status == 'ACTIVE'):
            print(f'The Server {server} already running.')
        else:
            print(f'running {server} ...')
            conn.compute.start_server(s)

    print('Operation completed.')
    pass


def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    print(f'Current status:')
    status()

    for server in SERVERLIST:
        s = conn.compute.find_server(server)  # find server
        ss = conn.compute.get_server(s.id)  # get server
        if(server == None):
            print(
                f'The Server {server} has not created. Please run this script with create parameter first.')
            return
        else:
            print(f'Stopping server {server}...')
            conn.compute.stop_server(s)

    print('Operation completed.')
    pass


def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    pass


def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    for server in SERVERLIST:
        s = conn.compute.find_server(server)
        if(s == None):
            print(
                f'The Server {server} has not created yet. Please run this script with create parameter first.')
            return
        else:
            ss = conn.compute.get_server(s.id)
            print(f'The status of server {server} is: {ss.status}')
    pass


### You should not modify anything below this line ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation',
                        help='One of "create", "run", "stop", "destroy", or "status"')
    args = parser.parse_args()
    operation = args.operation

    operations = {
        'create': create,
        'run': run,
        'stop': stop,
        'destroy': destroy,
        'status': status
    }

    action = operations.get(operation, lambda: print(
        '{}: no such operation'.format(operation)))
    action()
