import argparse
import openstack

conn = openstack.connect(cloud_name='openstack')
serverList = [ "bradcw1-app", "bradcw1-db", "bradcw1-web" ]

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'bradcw1-net'
SUBNET = 'bradcw1-subnet'
ROUTER = 'bradcw1-rtr'
SECURITY_GROUP = 'assignment2'
KEYPAIR = 'bradcw1-key'

public_net = conn.network.find_network(name_or_id='public-net')
floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
router = conn.network.find_router(ROUTER)
image = conn.compute.find_image(IMAGE)
flavour = conn.compute.find_flavor(FLAVOUR)
security_group = conn.network.find_security_group(SECURITY_GROUP)
keypair = conn.compute.find_keypair(KEYPAIR)   

network = conn.network.find_network(NETWORK)
router = conn.network.find_router(ROUTER)
subnet = conn.network.find_subnet(SUBNET)

def create():

    ''' Create a set of Openstack resources '''      

    # CREATE NETWORK
    print("Creating Network...")
    
    if conn.network.find_network(NETWORK) is None:
        network = conn.network.create_network(
            name=NETWORK)
        print("Network successfully created.")
    else:
        print("Network already exists.")
        pass

    # CREATE SUBNET
    print("Creating Subnet...")

    if conn.network.find_subnet(SUBNET) is None:
        subnet = conn.network.create_subnet(
            name=SUBNET,
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
        
        router = conn.network.create_router(
            name='bradcw1-rtr',
            external_gateway_info={ 'network_id' : public_net.id }
        )
        print("Router successfully created.")
        conn.network.add_interface_to_router(router, subnet.id)
    else:
        print("Router already exists.")
        pass


    # LAUNCH INSTANCES     

    for serverName in serverList:
        if conn.compute.find_server(name_or_id=serverName) is None:
            SERVER = serverName
            server = conn.compute.create_server(
            name=SERVER, image_id=image.id, flavor_id=flavour.id,
            networks=[{"uuid": network.id}], key_name=keypair.name, security_groups=[security_group])
            server = conn.compute.wait_for_server(server)
            print(serverName + " successfully created.")

            if serverName == "bradcw1-web":   
                web = conn.compute.find_server("bradcw1-web")
                conn.compute.wait_for_server(server)
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

    # DESTROY SERVERS
    for server in serverList:
        ser = conn.compute.find_server(name_or_id=server)
        
        if ser is not None:
            if server == 'bradcw1-web':
                dserver = conn.compute.get_server(ser)
                server_floating_ip = dserver['addresses'][NETWORK][1]['addr']

                print("Removing Floating IP")
                conn.compute.remove_floating_ip_from_server(dserver, server_floating_ip)
                
                print("Floating IP removed from " + ser.name)
                drop_ip = conn.network.find_ip(server_floating_ip)
                conn.network.delete_ip(drop_ip)
                
                print("IP Dropped")
                
            conn.compute.delete_server(ser)
            
            print(ser.name + " Destroyed.")
        else:
            print(server + " does not exist.") 

    # DESTROY ROUTER
    if router is not None:
        delInterface = conn.network.remove_interface_from_router(router, subnet.id)
        delRouter = conn.network.delete_router(router)
        print("Router Destroyed")
    else:
        print("Network does not exist.")        

    # DESTROY SUBNET
    if subnet is not None:
        delSubnet = conn.network.delete_subnet(subnet)
        print("Subnet Destroyed")
    else:
        print("Subnet does not exist.")
    
    # DESTROY NETWORK
    network = conn.network.find_network("bradcw1-net")
    if network is not None:
        delNetwork = conn.network.delete_network(network)
        print("Network Destroyed")
    else:
        print("Network does not exist.")   
    
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
