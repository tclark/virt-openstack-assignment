import argparse
import openstack

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
SERVERLIST = ['wangh21-web','wangh21-app','wangh21-db']
KEYPAIRNAME= 'hua'
NETWORK = 'wangh21-net'
SUBNET = '192.168.50.0/24'
ROUTER = 'wangh21-rtr'

conn = openstack.connect(cloud_name=’openstack’)



def create():
    ''' Create a set of Openstack resources '''
    conn.netowrk.find_network(NETWORK)==None? network = conn.network.create_network(name=NETWORK) : print(f'Network {NETWORK} already exists...')

    for server in SERVERLIST:
        is_exists = conn.compute.find_server(server)
        if(is_exists):
            print(f'The Server {server} already exists...')
        else:
            print(f'Start create {server}, please wait...')
            conn.compute.create_server(
                    name=server,
                    image_id=image.id,
                    flavor_id=flavor.id,
                    networks=[{"uuid": network}],
                    key_name='hua'
                    )

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
    pass

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
