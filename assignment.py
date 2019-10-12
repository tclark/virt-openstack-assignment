# project: 2019 S2 Virtualization assignment 2
# lecturer: Tom Clark
# student: Hua Wang
# date: 2019-09-14
# document ref: https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html

import argparse
import openstack

# declare constant
NETWORK = 'wangh21-net'
SUBNET = 'wangh21-subnet'
CIDR = '192.168.50.0/24'
ROUTER = 'wangh21-rtr'
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
SERVERLIST = ['wangh21-web', 'wangh21-app', 'wangh21-db']
SECURITYGROUP = 'assignment2'
KEYPAIRNAME = 'hua'

# connect to openstack
conn = openstack.connect(cloud_name='openstack')


def create():
    ''' Create a set of Openstack resources '''

    print('Preparing to create resources, please wait...')
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
            print(
                f'The server {server} has already exists. terminate operation...')
            break

        # add floating ip for wangh21-web server
        if(server == SERVERLIST[0]):
            print(f'The system is looking for floating ip address...')
            conn.compute.wait_for_server(s)
            # if the web server only already have one ip
            # add floating ip
            if(len(conn.compute.get_server(s.id)['addresses']['wangh21-net']) < 2):
                floating_ip = conn.network.create_ip(
                    floating_network_id=public_net.id).floating_ip_address
                conn.compute.add_floating_ip_to_server(s, floating_ip)
                print(f'Floating IP {floating_ip} added to {server}.')
    print('Operation completed.')


def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''

    for server in SERVERLIST:
        s = conn.compute.find_server(server)  # get server
        # 1. create server when server does not exists 2. check the server whehter running 3. start server
        if(s == None):
            print(
                f'The Server {server} has not created. Please run this script with [create] parameter first.')
        elif(conn.compute.get_server(conn.compute.find_server(server).id).status == 'ACTIVE'):
            print(f'The Server {server} already running.')
        else:
            print(f'running {server} ...')
            conn.compute.start_server(s)
            conn.compute.wait_for_server(s)
            print('Operation completed.')


def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''

    # display current status before stoping
    print(f'Current status:')
    status()

    for server in SERVERLIST:
        s = conn.compute.find_server(server)  # find server
        #ss = conn.compute.get_server(s.id)  # get server
        if(server == None):
            print(
                f'The Server {server} has not created. Please run this script with [create] parameter first.')
            break
        else:
            print(f'Stopping server {server}...')
            conn.compute.stop_server(s)
            conn.compute.wait_for_server(s)
            print('Operation completed.')
    


def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''

    # remove network, router and subnet interface
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet(SUBNET)
    router = conn.network.find_router(ROUTER)

    # delete the server list
    for server in SERVERLIST:
        s = conn.compute.find_server(server)
        if(s != None):
            print(f'Deleting server {server}...')
            conn.compute.delete_server(s)
            conn.compute.wait_for_server(s)
        else:
            print(f'Server {server} does not exists')
            break
        

    if network:
        print(f'clearing subnet interface...')
        conn.network.delete_subnet(subnet, ignore_missing=True)
        print(f'clearing network interface...')
        conn.network.delete_network(network, ignore_missing=True)
        print(f'Operation completed.')

    if router:
        print(f'clearing router interface...')
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(router, ignore_missing=True)


def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    for server in SERVERLIST:
        s = conn.compute.find_server(server)
        if(s == None):
            print(
                f'The Server {server} has not created yet. Please run this script with [create] parameter first.')
            break
        else:
            ss = conn.compute.get_server(s.id)
            print(f'The status of server {server} is: {ss.status}')


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
