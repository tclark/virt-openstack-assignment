import argparse
import openstack

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOR = 'c1.c1r1'
KEYPAIR = 'hayeska2-key'
SUBNET = 'hayeska2-subnet'
NETWORK = 'hayeska2-net'
ROUTER = 'hayeska2-router'
SECURITY_GROUP = 'assignment2'
PUBNET_NAME = 'public-net'
SERVER_NAMES = ['hayeska2-web', 'hayeska2-app', 'hayeska2-db']

conn = openstack.connect(cloud_name='openstack')

def create():
    ''' Create a set of Openstack resources '''
   # Create the Network
    if conn.network.find_network('hayeska2-net') is None:
        network = conn.network.create_network(
            name='hayeska2-net')
        print("Network has successfully been created.")
    else:
        print("Network already exists.")
        pass
    # Create the Subnet
     if conn.network.find_subnet('hayeska2-subnet') is None:
        subnet = conn.network.create_subnet(
            name='hayeska2-subnet',
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1')
        print("Subnet has been successfully created.")
    else:
        print("Subnet already exists.")
        pass
    
    # Create the Router
     if conn.network.find_router('hayeska2-router') is None:
        public_net = conn.network.find_network(name_or_id='public-net')
        router = conn.network.create_router(
            name='hayeska2-router',
            external_gateway_info={ 'network_id' : public_net.id }
        )
        print("Router has been successfully created.")
    else:
        print("Router already exists.")
        pass
    
    # Create the server
     for server in server_list:
        server = conn.compute.find_server(server)
        if server is None:
            print("Creating " + server + " the server")
            server = conn.compute.create_server(name=serv, image_id=image.id, flavor_id=flavour.id, networks=[{"uuid": network.id}], key_name=keypair.name)
            server = conn.compute.wait_for_server(server)
            conn.compute.add_security_group_to_server(server, sec_group)
            print(server + " Server has been created")
        else:
            print(server + " The server already exists")
            pass
        
        # Create and Assign floating IP address
          server = conn.compute.find_server('hayeska2-web')
          floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
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
