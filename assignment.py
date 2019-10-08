import argparse
import openstack
import subprocess

conn = openstack.connect(cloud_name='openstack')

def create():
	''' Create a set of Openstack resources '''
	
	'''create network'''
	schrsa1_network = conn.network.create_network(
        name='schrsa1-net')

	'''create subnet'''		
	schrsa1_subnet = conn.network.create_subnet(
        name='schrsa1-subnet',
        network_id=schrsa1_network.id,
        ip_version='4',
        cidr='192.168.50.0/24',
        gateway_ip='192.168.50.1')
		
	'''create router'''
	schrsa1_rtr = conn.network.create_router(
        name='schrsa1-rtr',
        admin_state_up=True,
        ext_gateway_net_id=public_net.id,
        ext_fixed_ips=[{"subnet_id": schrsa1_subnet.id}])

	
	'''create server'''
	IMAGE = 'ubuntu-16.04-x86_64'
	FLAVOUR = 'c1.c1r1'
	NETWORK = 'private-net'
	KEYPAIR = 'schrsa1-key'
	
	image = conn.compute.find_image(IMAGE)
	flavour = conn.compute.find_flavor(FLAVOUR)
	network = conn.network.find_network(NETWORK)
	keypair = conn.compute.find_keypair(KEYPAIR)
	
	SERVER = 'schrsa1-web'
	server = conn.compute.create_server(
	name=SERVER, image_id=image.id, flavor_id=flavour.id,
	networks=[{"uuid": network.id}], key_name=keypair.name)
	
	server = conn.compute.wait_for_server(server)
	
	public_net = conn.network.find_network('public-net')
	floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
	
	conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)
	pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
	subprocess.call(["openstack", "server", "start", "schrsa-web"])
	subprocess.call(["openstack", "server", "start", "schrsa-app"])
	subprocess.call(["openstack", "server", "start", "schrsa-db"])
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
	subprocess.call(["openstack", "server", "stop", "schrsa-web"])
	subprocess.call(["openstack", "server", "stop", "schrsa-app"])
	subprocess.call(["openstack", "server", "stop", "schrsa-db"])
    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
	subprocess.call(["openstack", "server", "delete", "schrsa1-db"])
	subprocess.call(["openstack", "server", "delete", "schrsa1-app"])
	subprocess.call(["openstack", "server", "delete", "schrsa1-web"])
	subprocess.call(["openstack", "floating", "ip", "delete", "public-net"])
	subprocess.call(["openstack", "router", "remove", "subnet", "schrsa-router", "schrsa1-subnet"])
	subprocess.call(["openstack", "router", "delete", "schrsa1-router"])
	subprocess.call(["openstack", "subnet", "delete", "schrsa1-subnet"])
	subprocess.call(["openstack", "network", "delete", "schrsa1-net"])
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
	subprocess.call(["openstack", "server", "show", "schrsa1-db"])
	subprocess.call(["openstack", "server", "show", "schrsa1-app"])
	subprocess.call(["openstack", "server", "show", "schrsa1-web"])
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