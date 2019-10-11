import argparse
import openstack


conn = openstack.connect(cloud_name='openstack', region_name ='nz-hlz-1a')

for server in conn.compute.servers():
   # pprint(server)
    

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOR = 'c1.c1r1'
NETWORK = 'chauw2-net'
SUBNET = 'chauw2-subnet'
ROUTER = 'chauw2-router'
KEYPAIR = 'chauw2key'
SECURITYGROUP = "assignment2"
PUBLICNET = 'public-net'
ALLSERVERSLIST = ['chauw2-web','chauw2-app','chauw2-db']
#WEB-SERVER = 'chauw2-web'
#APP-SERVER = 'chauw2-app'
#DB-SERVER = 'chauw2-db'

cidr = '192.168.10.0/24'
# Create openstack rescore
#https://docs.openstack.org/openstacksdk/latest/user/guides/compute.html
image = conn.compute.find_image(IMAGE)
flavor  = conn.compute.find_flavor(FLAVOR)
public_network = conn.compute.find_network(PUBLICNET)
keypair = conn.compute.find_keypair(KEYPAIR)
security_group = conn.network.find_security_group(SECURITYGROUP)
publicnet = conn.network.find_network(PUBLICNET)


def create():
    ''' Create a set of Openstack resources '''
    # Find network
    print("Searching Network...")
    network = conn.network.find_network(NETWORK)
    if network Exisit:
        print(NETWORK, 'exists')
    else
        print('Creating', NETWORK)
        network = conn.network.create_network(name=NETWORK)
    #Find Subnet
    subnet = conn.network.find_subnet(SUBNET)
    if subnet exist:
        print("Searching Subnet...")
    else
        subnet = conn.netowork.create_subnet(name=SUBNET,cidr,ip_verison=4
    
    # Find server
    print("Searching Server...")    
    if webserver = conn.compute.find_server(WEB-SERVER)
    if webser Exist:
        print(WEB-SERVER ,'exist')
    else
       server = conn.compute.create_server(
        name=SERVER_NAME, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name)

    server = conn.compute.wait_for_server(server)
             
    
# create server

    

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
