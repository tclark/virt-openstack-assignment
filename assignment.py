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

    print('Network created')

    subnet = conn.network.create_subnet(
            name='nichmr1-net',
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1'
            )

    print('Subnet created')

    #Create a router
    public_network = conn.network.find_network('public-net')
    router = conn.network.create_router(
            name='nichmr1-rtr',
            external_gateway_info={'network_id': public_network.id}            
            )
    conn.network.add_interface_to_router(router, subnet.id)

    print('Router created')
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

    #Get the stuff to delete
    network = conn.network.find_network('nichmr1-net')
    router = conn.network.find_router('nichmr1-rtr')
    subnet = conn.network.find_subnet('nichmr1-net')

    #Destroy the router
    conn.network.remove_interface_from_router(router, subnet.id)
    conn.network.delete_router(router)
    print('Router Destroyed')

    #Destroy the Subnets
    for subnet in network.subnet_ids:
        conn.network.delete_subnet(subnet, ignore_missing=False)
    print('Subnets Destroyed')

    #Destroy the Network
    conn.network.delete_network(network, ignore_missing=False)
    print('Network Destroyed')

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
