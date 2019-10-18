import argparse
import openstack
import time

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'coxts2-net'
KEYPAIR = 'coxts2-key'
SUBNET = 'coxts2-sub'
ROUTER = 'coxts2-rtr'
SERVER_WEB = 'coxts2-web'
SERVER_APP = 'coxts2-app'
SERVER_DB = 'coxts2-db'
SG = 'assignment2'
PN = 'public-net'

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
        conn.network.add_interface_to_router(router, subnet.id)
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
            security_groups=[security_group])
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
            security_groups=[security_group])
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
            security_groups=[security_group])
        server_db = conn.compute.wait_for_server(server_db)
    else:
        print(str(server_db.name)+" already exists")


def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    
    #Start web server
    
    server_web = conn.compute.find_server(SERVER_WEB)
    try:
        if not server_web:
            print(str(SERVER_WEB)+ " does not exist" )
        else:
            print("Starting server", str(SERVER_WEB))
            conn.compute.start_server(server_web)
    except:
        print(str(SERVER_WEB)+" is already running")
    
    #Start app server
    
    server_app = conn.compute.find_server(SERVER_APP)
    try:
        if not server_app:
            print(str(SERVER_APP)+ " does not exist" )
        else:
            print("Starting server", str(SERVER_APP))
            conn.compute.start_server(server_app)
    except:
        print(str(SERVER_APP)+" is already running")
    
    #Start db server
    
    server_db = conn.compute.find_server(SERVER_DB)
    try:
        if not server_db:
            print(str(SERVER_DB)+ " does not exist" )
        else:
            print("Starting server", str(SERVER_DB))
            conn.compute.start_server(server_db)    
    except:
        print(str(SERVER_DB)+" is already running")

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    
    #Stop web server
    
    server_web = conn.compute.find_server(SERVER_WEB)
    try:
        if not server_web:
            print(str(SERVER_WEB)+ " does not exist" )
        else:
            print("Stopping server", str(SERVER_WEB))
            conn.compute.stop_server(server_web)
    except:
        print(str(SERVER_WEB)+" is already shutdown")
    
    #Stop app server
    
    server_app = conn.compute.find_server(SERVER_APP) 
    try:
        if not server_app:
            print(str(SERVER_APP)+ " does not exist" )
        else:
            print("Stopping server", str(SERVER_APP))
            conn.compute.stop_server(server_app)
    except:
        print(str(SERVER_APP)+" is already shutdown")
    #Stop db server
    
    server_db = conn.compute.find_server(SERVER_DB)
    try:
        if not server_db:
            print(str(SERVER_DB)+ " does not exist" )
        else:
            print("Stopping server", str(SERVER_DB))
            conn.compute.stop_server(server_db)   
    except:
        print(str(SERVER_DB)+" is already shutdown")
    
    
def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    #destroy servers
    server_web = conn.compute.find_server(SERVER_WEB)
    server_app = conn.compute.find_server(SERVER_APP)
    server_db = conn.compute.find_server(SERVER_DB)
    router = conn.network.find_router(ROUTER)
    subnet = conn.network.find_subnet(SUBNET)
    network = conn.network.find_network(NETWORK)
    
        
    #web server destroy
    if not server_web:
        print(str(SERVER_WEB)+" does not exist")
    else:
        print(str(SERVER_WEB)+" is being annihilated")
        conn.compute.delete_server(server_web)
        
    #app server destroy
    if not server_app:
        print(str(SERVER_APP)+" does not exist")
    else:
        print(str(SERVER_APP)+" Is being annihilated")
        conn.compute.delete_server(server_app)
    
    #db server destroy
    if not server_db:
        print(str(SERVER_DB)+" does not exist")
    else:
        print(str(SERVER_DB)+" is being annihilated")
        conn.compute.delete_server(server_db)
        
    time.sleep(5)
    
    if subnet is not None:
        if router:
            try:
                print("removing interface from router")
                conn.network.remove_interface_from_router(router, subnet.id)
            except Exception:
                pass

        for port in conn.network.get_subnet_ports(subnet.id):
            print(str(port)+ " removing ports")
            conn.network.delete_port(port)
    
    
    floating_ip = conn.network.find_ip(floating_ip.floating_ip_address)
    if floating_ip:
        print("removing floating IP")
        conn.network.delete_ip(floating_ip)
    
    if router is not None:
        print("removing router")
        conn.network.delete_router(router)
    
    if subnet:
        print("removing subnet")
        conn.network.delete_subnet(subnet)
    
    if network is not None:
        print(str(network)+" network being removed")
        conn.network.delete_network(network)

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    
    server_web = conn.compute.find_server(SERVER_WEB)
    server_app = conn.compute.find_server(SERVER_APP)
    server_db = conn.compute.find_server(SERVER_DB)
    
    #web server status
    if not server_web:
        print(str(server_web.name)+" does not exist")
    else:
        server_web = conn.compute.get_server(server_web.id)
        print(str(SERVER_WEB)+" Status")
        server_web_status=server_web.status
        print(str(server_web_status))
            
    #app server status
    if not server_app:
        print(str(server_app.name)+" does not exist")
    else:
        server_app = conn.compute.get_server(server_app.id)
        print(str(SERVER_APP)+" Status")
        server_app_status=server_app.status
        print(str(server_app_status))    
    
    #db server status
    if not server_db:
        print(str(server_db.name)+" does not exist")
    else:
        server_db = conn.compute.get_server(server_db.id)
        print(str(SERVER_DB)+" Status")
        server_db_status=server_db.status
        print(str(server_db_status))    
    
    
    
    
    


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
