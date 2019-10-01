import argparse
import openstack

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

    if network is None:
        n_network = conn.network.create_network(name=NETWORK, admin_state_up=True)
        print(f'Created Network: {NETWORK}')
    else:
        print(f'Network: {NETWORK} Already Exists')

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
    print('running destroy function..')

    if network is not None:
        conn.network.delete_network(network)
        print(f'Network: {NETWORK} Deleted')
    else:
        print(f'Nework Already Deleted')

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
