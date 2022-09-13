# Adapted from examples on the openstack github https://github.com/openstack/openstacksdk/tree/master/examples/compute



import argparse
import openstack

def create_network(conn):
    print("Create Network:")

    westcl4_net = conn.network.create_network(
        name='westcl4-net'
    )
    print(westcl4_net)

    westcl4_subnet = conn.network.create_subnet(
        name='westcl4-subnet',
        network_id=westcl4_subnet.id,
        ip_version='4',
        cidr='192.168.50.0/24',
        gateway_ip='192.168.50.1')

    print(westcl4_subnet)




def create():
    ''' Create a set of Openstack resources '''


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
        'create'  : create,
        'run'     : run,
        'stop'    : stop,
        'destroy' : destroy,
        'status'  : status
        }

    action = operations.get(operation, lambda: print('{}: no such operation'.format(operation)))
    action()
