import argparse
import openstack

def create():
    ''' Create a set of Openstack resources '''
	conn = openstack.connect(cloud_name='openstack')
	
    print("Create Network:")

    network = conn.network.create_network(
        name='bradcw1-net')

    # print(network)

    # subnet = conn.network.create_subnet(
    #     name='openstacksdk-example-project-subnet',
    #     network_id=network.id,
    #     ip_version='4',
    #     cidr='192.168.50.0/24',
    #     gateway_ip='10.0.2.1')

    # print(example_subnet)
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
