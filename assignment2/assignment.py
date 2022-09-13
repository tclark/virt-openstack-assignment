# Adapted from examples on the openstack github https://github.com/openstack/openstacksdk/tree/master/examples/compute

import constant
import argparse
import openstack

conn = openstack.connect(cloud_name='openstack', region_name='nz-por-1')


def create_network():
    print("Creating network with name " + constant.NETWORK)

#check for network and create if non existing
    network = conn.network.find_network(constant.NETWORK)
    subnet = conn.network.find_subnet(constant.SUBNET)
    if (network is None):
        network = conn.network.create_network(
            name=constant.NETWORK
        )
    #print(westcl4_net)
#check for subnet and create if non existing
    if (subnet is None):
        subnet = conn.network.create_subnet(
        name=constant.SUBNET,
        network_id=network.id,
        ip_version='4',
        cidr='192.168.50.0/24',
        gateway_ip='192.168.50.1'
        )

    #print(USER_subnet)


def create():
    ''' Create a set of Openstack resources '''
    print("Create test")
    #print(constant.USER)
    create_network()

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
