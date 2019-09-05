import argparse
import openstack

IMAGE = 'ubuntu-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
KEYPAIR = 'mariadb'
NETWORK = 'gorda5-net'
SUBNET = 'gorda5-sub'
ROUTER = 'gorda5-rtr'
SERVER1 = 'gorda5-web'
SERVER2 = 'gorda5-app'
SERVER3 = 'gorda5-db'

conn = openstack.connect(cloud_name='openstack')

def create():
    ''' Create a set of Openstack resources '''
    if not conn.network.find_network(NETWORK):
        network = conn.network.create_network(name=NETWORK)
        subnet = conn.network.create_subnet(name=SUBNET, cidr='192.168.50.0/24', network_id=network.id, ip_version='4')
    else:
        print('Network already exist')

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
    if conn.network.find_network(NETWORK):
        network = conn.network.find_network(NETWORK)
        conn.network.delete_network(network)

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    servers = conn.compute.servers()
    for server in servers:
        print(server.name)


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
