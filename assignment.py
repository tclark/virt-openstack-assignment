import argparse
import openstack
import time


global conn 
conn = openstack.connect(cloud_name='openstack')
global serverList
serverList = ["dackja1-app", "dackja1-db", "dackja1-web"]
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'dackja1-net'
KEYPAIR = 'dackja1-key'
SECURITY_GROUP = 'assignment2'
SUBNET = 'dackja1-subnet'
ROUTER = 'dackja1-rtr'
PUBLICNET = 'public-net'

subnet = conn.network.find_subnet(SUBNET)
image = conn.compute.find_image(IMAGE)
flavour = conn.compute.find_flavor(FLAVOUR)
keypair = conn.compute.find_keypair(KEYPAIR)
security_group= conn.network.find_security_group(SECURITY_GROUP)
conn = openstack.connect(cloud_name='openstack')



def create():
    ''' Create a set of Openstack resources '''

    print ("connecting to Openstack")
    conn = openstack.connect(cloud_name='openstack')
    Network = conn.network.find_network(NETWORK)

    print (" creating network, name: dackja1 ")
    if Network is None:
       
        Network=conn.network.create_network(
            name= NETWORK)
        print("Network created")
    else:
        print("Network dackja1 already exists")
    pass

    if conn.network.find_subnet(SUBNET) is None:
        print ("creating subnet")
        subnet = conn.network.create_subnet(
            name = 'dackja1-subnet',
            network_id=Network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1'
        )
        print ("Subnet dackja1-subnet has been created")

    else:
        print ("Subnet already exists")
    pass

    print("Creating router")

    if conn.network.find_router(ROUTER) is None:
        public_net = conn.network.find_network(PUBLICNET)
        router = conn.network.create_router(
            name=ROUTER,
            external_gateway_info={'network_id': public_net.id}
            )
        conn.network.add_interface_to_router(router, subnet.id)
        print("Router dackja1-rtr has been created")

    else:
        print ("Router already exsits")
    pass

        



    for serverName in serverList:
        if conn.compute.find_server(name_or_id=serverName) is None:
            SERVER = serverName
            server =conn.compute.create_server(
            name=SERVER, image_id=image.id, flavor_id=flavour.id,
            networks=[{"uuid": Network.id}], key_name=keypair.name,security_groups=[{'name':security_group.name}])
            server = conn.compute.wait_for_server(server)
            print(serverName + " successfully created.")
        

            if serverName == "dackja1-web":
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
                web = conn.compute.find_server("dackja1-web")
                conn.compute.add_floating_ip_to_server(web, floating_ip.floating_ip_address)
                print("Floating IP " + str(floating_ip.floating_ip_address) + " given to dackja1-web.")
        else:
            print(serverName+ "already exists")
pass
def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''

    for name in serverList:
        server = conn.compute.find_server(name_or_id=name)
        if server is not None:
            ser = conn.compute.get_server(server)
            if ser.status == "SHUTOFF":
                conn.compute.start_server(server)
                print("started " + name)
            elif ser.status == "ACTIVE":
                print(name + " is running")

            else:
                print(name + " does not exist")

pass
    

def stop():
    for name in serverList:
        server = conn.compute.find_server(name_or_id=name)
        if server is not None:
            ser = conn.compute.get_server(server)
            if ser.status == "ACTIVE":
                conn.compute.stop_server(server)
                print(name + " has been stopped")
            elif ser.status == "SHUTOFF":
                print(name +" Is not running")

            else:
                print(name + "does not exist")

pass
    
   

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    Network = conn.network.find_network(NETWORK)




    


   
    for server in serverList:
        ser = conn.compute.find_server(name_or_id=server)
        if ser is not None:
            if ser == 'dackja1-web':
                web = conn.compute.get_server(ser)
                web_floating_ip = web['addresses'][Network][1]['addr']
                conn.compute.remove_floating_ip_from_server(web, web_floating_ip)
                deleteIp = conn.network.delete_ip(deleteIp)
            conn.compute.delete_server(ser)
            time.sleep(3)
           
            print(ser.name + " Destroyed.")
        else:
            print(server + " does not exist.")
       
    router = conn.network.find_router("dackja1-rtr")

   
    if router is not None:
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(router)
        print("Router Destroyed")
    else:
        print("Router does not exist")

    if subnet is not None: 
        conn.network.delete_subnet(subnet) 
        print('Subnet Destroyed')
    else:
        print('Subnet does not exist')

    if Network is not None: 
        conn.network.delete_network(Network) 
        print('Network Destroyed') 
    else:
        print('Network does not exist')



   

pass

    

def status():
    for server in serverList:
        serverid = conn.compute.find_server(name_or_id=server)
        if serverid is None:
            print(server + " does not exist.")
        elif serverid is not None:
            ser = conn.compute.get_server(serverid)
            print("Name: " + ser.name + "\n" 
                "Status: " + ser.status) 
            for value in ser.addresses[NETWORK]:
                print("IP: " + value["addr"])
            print("\n") 
   
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

