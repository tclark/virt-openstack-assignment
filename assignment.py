import argparse
import openstack
import time

conn = openstack.connect(cloud_name="openstack")

IMAGE = "ubuntu-minimal-16.04-x86_64"
FLAVOUR = "c1.c1r1"
NETWORK = "mccacj3-net"
SECURITY_GROUP = "assignment2"
SUBNET = "mccacj3-subnet"
ROUTER = "mccacj3-rtr"
KEYPAIR = "Chas"
SERVER_LIST = ['mccacj3-web', 'mccacj3-app', 'mccacj3-db']
SUBNET_IP = '192.168.50.0/24'


network = conn.network.find_network(NETWORK)
router = conn.network.find_router(ROUTER, ignore_missing=True)
subnet = conn.network.find_subnet(SUBNET)
image = conn.compute.find_image(IMAGE)
flavour = conn.compute.find_flavor(FLAVOUR)
keypair = conn.compute.find_keypair(KEYPAIR)


def create():

    if network is None:
        Network = conn.network.create_network(name=NETWORK, admin_state_up=True)
        print('Created Network: '+ NETWORK)
    else:
        print('Network: ' + NETWORK +' already Exists')

    if subnet is None:
        Subnet = conn.network.create_subnet(name=SUBNET, network_id=Network.id, ip_version='4', cidr=SUBNET_IP)
        print('Created Subnet: '+ SUBNET)
    else:
        print('Subnet: '+SUBNET+' already Exists')

    router = conn.network.find_router(ROUTER, ignore_missing=True)
    if router is None:
        print('Attempting to create router '+ROUTER)
        router = conn.network.create_router(name=ROUTER, external_gateway_info={"network_id" : conn.network.find_network("public-net").id})
        Subnet = conn.network.find_subnet(SUBNET)
        conn.network.add_interface_to_router(router,Subnet.id)


        print("Router "+ ROUTER +" has been created successfully.")

    for name in SERVER_LIST:
        server = conn.compute.find_server(name)
        print("Trying to create server "+name)
        if server is None:
            new_server = conn.compute.wait_for_server(conn.compute.create_server(name=name,
                image_id=image.id,
                flavor_id=flavour.id,
                networks=[{"uuid": Network.id}],
                key_name=keypair.name,
                security_groups=[{"name": SECURITY_GROUP}]))
            if name == "mccacj3-web":
                floating_ip = conn.network.create_ip(floating_network_id=conn.network.find_network('public-net').id)
                conn.compute.add_floating_ip_to_server(new_server, address=floating_ip.floating_ip_address)
            print("Server "+name+" created succesfully.")
        else:
            print("Error! "+name+" already exists.")


def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
     for name in SERVER_LIST:
        print("Starting server "+name)
        server = conn.compute.find_server(name)
        if server is None:
            print("Error! Server "+name+" could not be found")
        else:
            if conn.compute.get_server(server).status != "ACTIVE":
                conn.compute.start_server(server)
                print("Server "+name+" has started successfully.")
            else:
                print("Server "+name+" is already running")



def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    for name in SERVER_LIST:
        print("Stopping server "+name)
        server = conn.compute.find_server(name)
        if server is None:
            print("Error! "+name+" not found. ")
        else:
            if conn.compute.get_server(server).status == "ACTIVE":
                conn.compute.stop_server(server)
                print("Server "+name+" has stopped successfully.")
            else:
                print("Server "+name+" is not active.")

def destroy():
    ''' Tear down the set of Openstack resources
    produced by the create action
    '''
    for name in SERVER_LIST:
        server = conn.compute.find_server(name)
        if server is not None:
            print("Attempting to destroy server "+name)
            conn.compute.delete_server(server)
            print("Destroyed server "+name)

        router = conn.network.find_router(ROUTER, ignore_missing=True)
    if router is not None:
        print("Attempting to destroy router "+ROUTER)
        network = conn.network.find_network(NETWORK, ignore_missing=True)
        subnet = conn.network.find_subnet(SUBNET)
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(conn.network.find_router(ROUTER, ignore_missing=True))
        print("Router "+ROUTER+" was destroyed.")
        network = conn.network.find_network(NETWORK, ignore_missing=True)
    if network is not None:
        print("Attempting to destroy network "+NETWORK)
        time.sleep(3)
        conn.network.delete_network(network)
        print("Network "+NETWORK+" was destroyed")

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    for name in SERVER_LIST:
         server = conn.compute.find_server(name)
         if server is None:
             print("Error! Server "+name+" not found.")
         else:
             server = conn.compute.get_server(server)
             ip_address = server.addresses[NETWORK][0]["addr"]
             version = server.addresses[NETWORK][0]["version"]
             IPtype = server.addresses[NETWORK][0]["OS-EXT-IPS:type"]
             if ip_address is None:
                 ip_address = "Not found"
             print("Server name: "+name)
             print("Server IP addresses: "+ip_address)
             print("Server status: "+server.status)
             print("IP version: "+str(version))
             print("IP Address type :"+IPtype)
             print("---------------------------")

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
   
                                                                                                                                                                                                                                                         16,0-1        Top

