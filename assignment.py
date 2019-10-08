import argparse
import openstack

conn = openstack.connect(cloud_name='openstack')

def create():
    ''' Create a set of Openstack resources '''
	
    '''create network'''
    schrsa1_network = conn.network.find_network('schrsa1-net')
    if schrsa1_network is None:
        schrsa1_network = conn.network.create_network(name='schrsa1-net')
	
    '''create subnet'''		
    schrsa1_subnet = conn.network.find_subnet('schrsa1-subnet')
    if schrsa1_subnet is None:
        schrsa1_subnet = conn.network.create_subnet(
        name='schrsa1-subnet',
        network_id=schrsa1_network.id,
        ip_version='4',
        cidr='192.168.50.0/24',
        gateway_ip='192.168.50.1')
		
    '''create router'''
    schrsa1_rtr = conn.network.find_router('schrsa1-rtr')
    if schrsa1_rtr is None:
        schrsa1_rtr = conn.network.create_router(name='schrsa1-rtr', admin_state_up=True, ext_gateway_net_id=public_net.id)

	
    '''create server'''
    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'
    NETWORK = 'private-net'
    KEYPAIR = 'schrsa1-key'
	
    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    network = conn.network.find_network(NETWORK)
    keypair = conn.compute.find_keypair(KEYPAIR)
	
    SERVER = 'schrsa1-web'
	
    server = conn.compute.find_server('schrsa1-web')
    if server is None:
        server = conn.compute.create_server(name=SERVER, image_id=image.id, flavor_id=flavour.id, networks=[{"uuid": network.id}], key_name=keypair.name)

    server = conn.compute.wait_for_server(server)
	
    public_net = conn.network.find_network('public-net')
    #floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
	
    conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)
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
