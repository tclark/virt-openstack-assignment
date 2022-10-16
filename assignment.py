import argparse
import openstack

conn = openstack.connect(cloud_name='openstack')

prefix = 'hookke2'
IMAGE = 'ubuntu-minimal-22.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = prefix + '-net'
SUBNET = prefix + '-subnet'
ROUTER = prefix + '-rtr'
KEYPAIR = prefix + '-key'
SECURITY_GROUP = 'assignment2'
CIDR = '192.168.50.0/24'
SERVERS = [prefix + '-web',prefix + '-app',prefix + '-db']
WEBSERVER = prefix + '-web'

image = conn.compute.find_image(IMAGE)
flavour = conn.compute.find_flavor(FLAVOUR)
keypair = conn.compute.find_keypair(KEYPAIR)
public_net = conn.network.find_network ('public-net')
securityGroup = conn.network.find_security_group(SECURITY_GROUP)

netwk = conn.network.find_network(NETWORK)
subnt = conn.network.find_subnet(SUBNET)
routr = conn.network.find_router(ROUTER)

def create():
    ''' Create a set of Openstack resources '''
   
    # Look for a network. If no network exists, create one   
    print("Checking network...")
    if netwk is None:
        network = conn.network.create_network(name=NETWORK)
        print("Network ", NETWORK, "has been created")
    else:
        print("Network ", NETWORK, "already exists")
    
    # Look for subnet. If no subnet exists, create one
    print("Checking subnet...")
    if subnt is None:
        subnet = conn.network.create_subnet(name=SUBNET, network_id=network.id, cidr=CIDR, ip_version='4')
        print("Subnet", SUBNET, "has been created")
    else:
        print("Subnet", SUBNET, "already exists")
    
    # Look for a router. If no router exists, create one and assign the external gateway. Connect private network to router
    print("Checking for router...")
    if routr is None:
        router = conn.network.create_router(name=ROUTER, external_gateway_info={"network_id": public_net.id})
        print("Router", ROUTER, "has been created")
        conn.network.add_interface_to_router(router,subnet.id)
    else:
        print("Router", ROUTER, "already exists")
    
    
    # Iterate through SERVERS. If server doesn't exist, create it. If the server is the WEBSERVER, associate a floating IP for external network access.
    for server in SERVERS:
        serverName = server
        serverFind = conn.compute.find_server(serverName)
        print("Checking for servers...")
        if serverFind is None:
            print("Creating", serverName)
            server = conn.compute.create_server(name=serverName, image_id=image.id, flavor_id=flavour.id, networks=[{"uuid": network.id}], key_name=keypair.name, security_groups=[{"name": securityGroup.id}])
            server = conn.compute.wait_for_server(server)
            print("Server",server.name, server.id, "created")
            if serverName == WEBSERVER:
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
                conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)
                print("Associating floating ip address:", floating_ip.floating_ip_address,"to webserver")
            else:
                print("Server",serverName,"No floating IP associated")
        else:
            print("Server",serverName, serverFind.id,"already exists")
   
 #    pass


def run(): 
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''

    print("Running...")
    print("Checking for stopped servers...")
    # Iterate through SERVERS. If server exists, and has status 'shutoff', start it. 
    # If server is "WEBSERVER" optional choice to reassociate floating IP address 
    for server in SERVERS:
        serverName = server
        serverFind = conn.compute.find_server(serverName)
        if serverFind is not None:
            server = conn.compute.get_server(serverFind)

            # Un-comment below section to reassociate a floating IP address on start-up
#           if serverName == WEBSERVER:
#                avail_floatingIP = conn.network.find_available_ip()
#                print("Checking for available ip address")
#                try:
#                    if avail_floatingIP:
#                        conn.compute.add_floating_ip_to_server(server, avail_floatingIP.floating_ip_address)
#                        print("Associating floating ip address:",avail_floatingIP.floating_ip_address,"to webserver")     
#                    else:
#                        new_floatingIP = conn.network.create_ip(floating_network_id=public_net.id)
#                        conn.compute.add_floating_ip_to_server(server, new_floatingIP.floating_ip_address)
#                        print("Associating floating ip address:", new_floatingIP.floating_ip_address,"to webserver")
#                except:
#                    print("Error: Check status of floating ip address")

            if server.status == "ACTIVE" or server.status == "BUILD":
                print("The server",serverName,"is already running or currently building")
            elif server.status == "SHUTOFF":
                serverStart = conn.compute.start_server(server)
                server = conn.compute.wait_for_server(server)
                print(serverName,"is now running")
            else:
                print("Status of",serverName,"is",server.status,". No action taken")     
        elif serverFind is None:
            print("The server",serverName,"does not exist")
        else:
            print("There seems to be an issue, check your servers")


#    pass


def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
   
    print("Stopping...")
    # Iterate through SERVERS. If server exists, and has status 'active' or 'build', stop it.
    # If server is "WEBSERVER" optional choice to disassociate floating IP address

    for server in SERVERS:
        serverName = server
        serverFind = conn.compute.find_server(serverName)
        if serverFind is not None:
            server = conn.compute.get_server(serverFind)
            if server.status == "SHUTOFF":
                print("The server",serverName,"is already stopped")                
            elif server.status == "ACTIVE" or server.status == "BUILD":
                print("Stopping server",serverName)
                serverStop = conn.compute.stop_server(server)
                server = conn.compute.wait_for_server(server)

            # Un-comment below section to disassociate a floating IP address on shutdown
#                if serverName == WEBSERVER:
#                    try:
#                        webFloatIP = server["addresses"][NETWORK][1]["addr"]
#                        floatingIP = conn.network.find_ip(webFloatIP)
#                    except:
#                        print("No floating ip found")
#                    if floatingIP:
#                        print("Disassociating floating ip address:",floatingIP.floating_ip_address,"from webserver")
#                        conn.compute.remove_floating_ip_from_server(server,webFloatIP)
#                    else:
#                       print("No floating ip currently associated")
            else:
                print("Status of",serverName,"is",server.status,". No action taken")
        elif serverFind is None:
            print("The server",serverName,"does not exist")
        else:
            print("There seems to be an issue, check your servers")

#   pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action

    '''
    # Iterate through SERVERS. If server exists, destroy it.
    # If server is "WEBSERVER" diassociate floating IP address

    for server in SERVERS:
        serverName = server
        serverFind = conn.compute.find_server(serverName)
        if serverFind is not None:
            server = conn.compute.get_server(serverFind)
            if serverName == WEBSERVER:
                try:
                    webFloatIP = server["addresses"][NETWORK][1]["addr"]
                    floatingIP = conn.network.find_ip(webFloatIP) 
                    if floatingIP:
                        print("Dissassociating floating ip address:",floatingIP.floating_ip_address,"from webserver")
                        print("Deleting floating ip")
                        conn.network.delete_ip(floatingIP)
                except:
                    print("No floating ip found")
            print("Destroying server:",serverName)
            conn.compute.delete_server(server)
            server = conn.compute.wait_for_server(server)
        else:
            print("The server",serverName,"doesn't exist so cannot be destroyed")
    
    # If router exists, remove the interface and destroy it
    if routr:
        conn.network.remove_interface_from_router(routr, subnt.id)
        conn.network.delete_router(routr)
        print("Router",routr.name,"has been deleted")
    else:
        print("Router does not exist")
    
    # If network exists, delete it. This includes subnets within the network
    if netwk:
        conn.network.delete_network(netwk)
        print("Network", netwk.name,"and subnet",subnt.name,"have been deleted")
    else:
        print("Network does not exist")
        
#   pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    # Iterate through SERVERS. For each server found, provide it's name, status, and any associated IP addresses
    for server in SERVERS:
        serverName = server
        serverFind = conn.compute.find_server(serverName)
        if serverFind:
            server = conn.compute.get_server(serverFind)
            print("-------------------------------")
            print("Server name:",serverName)
            
            print("Server status:",server.status)
            
            try:
                webFixedIP = server["addresses"][NETWORK][0]["addr"]
                print("Fixed ip address:",webFixedIP)
               
            except:
                print("Fixed IP address not found")
            try:
                webFloatIP = server["addresses"][NETWORK][1]["addr"]
                print("Floating IP address:",webFloatIP)
                
            except:
                print("Floating IP address not found")
            print("")
            print("-------------------------------")
        else:
            print("Server",serverName,"not found")
#   pass

#create()
#run()
#stop()
#status()
destroy()

### You should not modify anything below this line ###
#if __name__ == '__main__':
#    parser = argparse.ArgumentParser()
#    parser.add_argument('operation',
#                        help='One of "create", "run", "stop", "destroy", or "status"')
#    args = parser.parse_args()
#    operation = args.operation

#    operations = {
#        'create'  : create,
#        'run'     : run,
#        'stop'    : stop,
#        'destroy' : destroy,
#        'status'  : status
#        }

#    action = operations.get(operation, lambda: print('{}: no such operation'.format(operation)))
#    action()
