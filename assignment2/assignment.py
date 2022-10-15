# Adapted from examples on the openstack github https://github.com/openstack/openstacksdk/tree/master/examples/compute

import constant
import argparse
import openstack

conn = openstack.connect(cloud_name='openstack', region_name='nz-por-1')

# checking for existing networks
def getNetwork():
    network = conn.network.find_network(constant.NETWORK)
    return network

def getSubnet():
    subnet = conn.network.find_subnet(constant.SUBNET)
    return subnet

def getRouter():
    router = conn.network.find_router(constant.ROUTERNAME)
    return router

def create_network():
    print("Checking network status...")

    #define network variables
    network = getNetwork()
    subnet = getSubnet()
    router = getRouter()

    print(router)

    #check for network and create if non existing
    if (network is None):
        network = conn.network.create_network(
            name=constant.NETWORK
        )
        print("Created network with name " + constant.NETWORK)

    # check for subnet and create if non existing
    if (subnet is None):
        subnet = conn.network.create_subnet(
        name=constant.SUBNET,
        network_id=network.id,
        ip_version='4',
        cidr=constant.CIDR,
        gateway_ip=constant.GATEWAY_IP
        )
        print("Created subnet with name " + constant.SUBNET)

    # Check for router and create if non existing
    if (router is None):   
        try:
            router = conn.network.create_router(
                name= "westcl4-net", external_gateway_info={"network_id": conn.network.find_network("public-net").id})
            print("Created router with name ")
        except:
            print("Router creation failed")
        router = conn.network.add_interface_to_router(router,subnet_id=subnet.id)
        print(router)

def get_app():
    app = conn.compute.find_server(constant.APP_NAME)
    return app

def create_compute():
    print("Checking compute status...")
    return

def create():
    ''' Create a set of Openstack resources '''
    print("Create test")
    # print(constant.USER)
    create_network()
    create_compute()
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
