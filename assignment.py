import argparse
import openstack

IMAGE = 'ubuntu-minimal-22.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = ''
KEYPAIR = 'nichmr1-key'



def create():
    ''' Create a set of Openstack resources '''
    #Establish a connection to catalystcloud
    conn = openstack.connect(cloud_name='catalystcloud')
    
    #Create a network
    network = conn.network.create_network(
            name='nichmr1-net'
            )

    print(network)

    subnet = conn.network.create_subnet(
            name='nichmr1-net',
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1'
            )

    print(subnet)
    #Create a router

    #Create a floating IP address


    #Create three servers



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
    conn = openstack.connect(cloud_name='catalystcloud')

    #Delete Networking Stuff
    network = conn.network.find_network(
            'nichmr1-net'
            )

    for subnet in network.subnet_ids:
        conn.network.delete_subnet(subnet, ignore_missing=False)
    conn.network.delete_network(network, ignore_missing=False)

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
