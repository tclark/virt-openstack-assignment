import argparse
import openstack


#create connection to openstack
conn = openstack.connect(cloudname='openstack')
def create():
    
    #collect variables
    flavour = conn.compute.find_flavor('c1.c1r1')
    image = conn.compute.find_image('ubuntu-minimal-16.04-x86_64')
    keypair = conn.compute.find_keypair('kate')
    network = conn.network.find_network('shinrl1-net')
    router = conn.network.find_router('shinrl1-rtr')

    #create network

    if not network:
        network = conn.network.create_network(name='shinrl1-net')
        print(network)
        subnet='shinrl1-subnet',
        network_id=network.id,
        ip_version='4',
        cidr='192.168.50.0/24'
        gateway_ip='192.168.50.1'
        print("Network created ^_^")
    else:
        print("Borked")
    pass

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
    def list_networks(conn):
        print("List Networks:")

    for network in conn.network.networks():
        print(network)

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
