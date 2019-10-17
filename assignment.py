import argparse
import openstack

IMAGE = 'ubuntu-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'coxts2-net'
KEYPAIR = 'coxts2-key'
SUBNET = 'coxts2-sub'
ROUTER = 'coxts2-rtr'
SERVER_WEB = 'coxts2-web'
SERVER_APP = 'coxts2-app'
SERVER_DB = 'coxts2-db'
SG = 'assignment2'
PN = 'coxts2-net'

conn = openstack.connect(cloud_name='openstack')

def create():
    ''' Create a set of Openstack resources '''

image = conn.compute.find_image(IMAGE)
flavor = conn.compute.find_flavor(FLAVOUR)
network = conn.network.find_network(NETWORK)
keypair = conn.compute.find_keypair(KEYPAIR)
security_group = conn.network.find_security_group(SG)
public_net = conn.network.find_network(PN)

#Create Network

network = conn.network.find_network(NETWORK)

if not network:
    print("Constructing "+str(NETWORK)+" Network:")
    network = conn.network.create_network(name=NETWORK)
else:
    print("Network "+str(network.name)+" exists")

#Create Subnet

subnet = conn.network.find_subnet(SUBNET)

if not subnet:
    print("Constructing "+str(SUBNET)+" Subnet")
    subnet = conn.network.create_subnet(
        name=SUBNET,
        network_id=network.id,
        ip_version='4',
        cidr='192.168.50.0/24',
        gateway_ip='192.168.50.1')
else:
    print("Subnet "+str(subnet.name)+" exists")


#Create Router

router = conn.network.find_router(ROUTER)

if not router:
    print("Constructing "+str(ROUTER)+ " Router")
    router = conn.network.create_router(name=ROUTER,external_gateway_info={"network_id": public_net.id})
    conn.network.router_add_to_interface(router, subnet.id)
else:
    print(str(router.name)+ " already exists")


#Create Floating IP address

print("Getting floating IP")
floating_ip = conn.network.create_ip(floating_network_id=public_net.id)


#Create Web Server

server_web = conn.compute.find_server(SERVER_WEB)

if not server_web:
    print("Constructing "+str(SERVER_WEB)+" server")
    server_web = conn.compute.create_server(
        name=SERVER_WEB, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name,
        security_groups=(security_group))
    server_web = conn.compute.wait_for_server(server_web)
    print("Assigning floating IP to ", str(SERVER_WEB))
    conn.compute.add_floating_ip_to_server(server_web, floating_ip.floating_ip_address)
else:
    print(str(server_web.name)+" already exists")


#Create App Server

server_app = conn.compute.find_server(SERVER_APP)

if not server_app:
    print("Constructing "+str(SERVER_APP)+" server")
    server_app = conn.compute.create_server(
        name=SERVER_APP, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name,
        security_groups=(security_group))
    server_app = conn.compute.wait_for_server(server_app)
else:
    print(str(server_app.name)+ " already exists")


#Create db Server

server_db = conn.compute.find_server(SERVER_DB)

if not server_db:
    print("Constructing "+str(SERVER_DB)+" server")
    server_db = conn.compute.create_server(
        name=SERVER_DB, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name,
        security_groups=(security_group))
    server_db = conn.compute.wait_for_server(server_db)
else:
    print(str(server_db.name)+" already exists")


def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''

    #Start web server

server_web = conn.compute.find_server(SERVER_WEB)

if not server_web:
    print(str(SERVER_WEB)+ " does not exist" )
else:
    print("Starting server", str(SERVER_WEB))
    conn.compute.start_server(SERVER_WEB)


#Start app server

server_app = conn.compute.find_server(SERVER_APP)

if not server_app:
    print(str(SERVER_APP)+ " does not exist" )
else:
    print("Starting server", str(SERVER_APP))
    conn.compute.start_server(SERVER_APP)


#Start db server

server_db = conn.compute.find_server(SERVER_DB)

if not server_db:
    print(str(SERVER_DB)+ " does not exist" )
else:
    print("Starting server", str(SERVER_DB))
    conn.compute.start_server(SERVER_DB)    


def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''

#Stop web server

server_web = conn.compute.find_server(SERVER_WEB)

if not server_web:
    print(str(SERVER_WEB)+ " does not exist" )
else:
    print("Stopping server", str(SERVER_WEB))
    conn.compute.stop_server(SERVER_WEB)


#Stop app server

server_app = conn.compute.find_server(SERVER_APP) 

if not server_app:
    print(str(SERVER_APP)+ " does not exist" )
else:
    print("Stopping server", str(SERVER_APP))
    conn.compute.stop_server(SERVER_APP)


#Stop db server

server_db = conn.compute.find_server(SERVER_DB)

if not server_db:
    print(str(SERVER_DB)+ " does not exist" )
else:
    print("Stopping server", str(SERVER_DB))
    conn.compute.stop_server(SERVER_DB)   


def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    

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
