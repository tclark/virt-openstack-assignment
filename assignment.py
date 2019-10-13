import argparse
import openstack


global conn 
conn = openstack.connect(cloud_name='openstack')
global serverList
serverList = ["dackja1-app", "dackja1-db", "dackja1-web"]

def create():
    ''' Create a set of Openstack resources '''

    print ("connecting to Openstack")
    conn = openstack.connect(cloud_name='openstack')

    print (" creating network, name: dackja1 ")
    if conn.network.find_network('dackja1-net') is None:
       
        network=conn.network.create_network(
            name='dackja1-net')
        print("Network created")
    else:
        print("Network dackja1 already exists")
    pass

    if conn.network.find_subnet('dackja1-subnet') is None:
        print ("creating subnet")
        subnet = conn.network.create_subnet(
            name = 'dackja1-subnet',
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1'
        )
        print ("Subnet dackja1-subnet has been created")

    else:
        print ("Subnet already exists")
    pass

    print("Creating router")

    if conn.network.find_router('dackja1-rtr') is None:
        public_net = conn.network.find_network('public-net')
        router = conn.network.create_router(
            name='dackja1-rtr',
            external_gateway_info={'network_id': public_net.id}
            )
        print("Router dackja1-rtr has been created")

    else:
        print ("Router already exsits")
    pass

        

    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'
    Network = 'private-net'
    KEYPAIR = 'dackja1-key'
    SECURITY_GROUP = 'assignment2'

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    network = conn.network.find_network(Network)
    keypair = conn.compute.find_keypair(KEYPAIR)
    security_group= conn.network.find_security_group(SECURITY_GROUP)

    for serverName in serverList:
        if conn.compute.find_server(name_or_id=serverName) is None:
            SERVER = serverName
            server =conn.compute.create_server(
            name=SERVER, image_id=image.id, flavor_id=flavour.id,
            networks=[{"uuid": network.id}], key_name=keypair.name,ecurity_groups=[security_group])
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

    conn = openstack.connect(cloud_name='openstack')
 
    network = conn.network.find_network("dackja1-net")

    if network is not None:
        
        delNetwork = conn.network.delete_network(network)
        print("Network Destroyed")
    else:
        print("Network does not exist")


    router = conn.network.find_router("dackja1-rtr")
    if router is not None:
        delRouter = conn.network.delete_router(router)
        print("Router Destroyed")
    else:
        print("Router does not exist")

    for server in serverList:
        ser = conn.compute.find_server(name_or_id=server)
        if ser is not None:
            conn.compute.delete_server(ser)
            print(ser.name + " Destroyed.")
        else:
            print(server + " does not exist.")

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
            for value in ser.addresses["private-net"]:
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

