import argparse
import openstack

global conn 
conn = openstack.connect(cloud_name='openstack')
global serverList
serverList = [ "bradcw1-app", "bradcw1-db", "bradcw1-web" ]


def create():

    ''' Create a set of Openstack resources '''      

    # CREATE NETWORK
    print("Creating Network...")
    
    if conn.network.find_network('bradcw1-net') is None:
        network = conn.network.create_network(
            name='bradcw1-net')
        print("Network successfully created.")
    else:
        print("Network already exists.")
        pass

    # CREATE SUBNET
    print("Creating Subnet...")

    if conn.network.find_subnet('bradcw1-subnet') is None:
        subnet = conn.network.create_subnet(
            name='bradcw1-subnet',
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1')
        print("Subnet successfully created.")
    else:
        print("Subnet already exists.")
        pass

    # CREATE ROUTER
    print("Creating Router...")

    if conn.network.find_router('bradcw1-rtr') is None:
        public_net = conn.network.find_network(name_or_id='public-net')
        router = conn.network.create_router(
            name='bradcw1-rtr',
            external_gateway_info={ 'network_id' : public_net.id }
        )
        print("Router successfully created.")
    else:
        print("Router already exists.")
        pass


    # LAUNCH INSTANCES

    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'
    NETWORK = 'private-net'
    KEYPAIR = 'bradcw1-key'

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    network = conn.network.find_network(NETWORK)
    keypair = conn.compute.find_keypair(KEYPAIR)    

    for serverName in serverList:
        if conn.compute.find_server(name_or_id=serverName) is None:
            SERVER = serverName
            server = conn.compute.create_server(
            name=SERVER, image_id=image.id, flavor_id=flavour.id,
            networks=[{"uuid": network.id}], key_name=keypair.name)
            server = conn.compute.wait_for_server(server)
            print(serverName + " successfully created.")

            if serverName == "bradcw1-web":
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)    
                web = conn.compute.find_server("bradcw1-web")
                conn.compute.add_floating_ip_to_server(web, floating_ip.floating_ip_address)
                print("Floating IP " + str(floating_ip.floating_ip_address) + " applied to bradcw1-web.")

        else:
            print(serverName + " already exists.")
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
                print(name + " starting up...")
                conn.compute.start_server(ser)
                print(name + " running.")
            elif ser.status == "ACTIVE":
                print(name + " is already running.")            
        else:
            print(name + " does not exist.")

    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    for name in serverList:        
            server = conn.compute.find_server(name_or_id=name)
            if server is not None:
                ser = conn.compute.get_server(server)
                if ser.status == "ACTIVE":
                    print(name + " stopping...")
                    conn.compute.stop_server(ser)
                    print(name + " stopped.")
                elif ser.status == "SHUTOFF":
                    print(name + " is already off.")            
            else:
                print(name + " does not exist.")

    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''

    # DESTROY NETWORK
    network = conn.network.find_network("bradcw1-net")
    if network is not None:
        delNetwork = conn.network.delete_network(network)
        print("Network Destroyed")
    else:
        print("Network does not exist.")

    # DESTROY ROUTER
    router = conn.network.find_router("bradcw1-rtr")
    if router is not None:
        delRouter = conn.network.delete_router(router)
        print("Router Destroyed")
    else:
        print("Network does not exist.")
    
    # DESTROY SERVERS
    for server in serverList:
        ser = conn.compute.find_server(name_or_id=server)
        if ser is not None:
            conn.compute.delete_server(ser)
            print(ser.name + " Destroyed.")
        else:
            print(server + " does not exist.")

    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''

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
