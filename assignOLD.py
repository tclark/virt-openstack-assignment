import argparse
import openstack
conn = openstack.connect(cloud_name='openstack')

def create(conn):
    ''' Create a set of Openstack resources '''
    #openstack network create --internal parkelj1-net
    #openstack subnet create --network parkelj1-net --subnet-range 192.168.50.0/24 parkelj1-subnet
    ####work out hwo to do this with python - create network called parkelj1 and create subnet
    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'
#    NETWORK = 'parkelj1-net'
    KEYPAIR = 'parkelj1-key'
    floating_ip is None

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    server_names = ['parkelj1-app','parkelj1-db','parkelj1-web']
    
# NETWORK: Check for network and create if not present
    print(">>> Checking for existing networks...")
    network = conn.network.find_network('parkelj1-net')
    if network is None:
        print(">>> No existing network found, creating...")
        network = conn.network.create_network(name='parkelj1-net')
    else:
        print(">>> Existing network found, continuing...")

# SECURITY GROUP: Check for security group, so we can use upon server creation
    print(">>> Checking for security group 'assignment2'...")
    security_group = conn.network.find_security_group(name_or_id='assignment2')
    if security_group is None:
        print(">>> Unable to find preferred security group, continuing...")

# SUBNET: Check for subnet and create if not present
    print(">>> Checking for existing subnets...")
    subnet = conn.network.find_subnet('parkelj1-subnet')
    if subnet is None:
        print(">>> Creating subnet...")
        subnet = conn.network.create_subnet(
            name='parkelj1-subnet',
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1')
    else:
        print(">>> Subnet exists, continuing...")


# SERVER: Check for web server and create if not present
    for server_name in server_names:
        print(">>> Checking for existing " + server_name + " server...")
        server = conn.compute.find_server(server_name)
        if server is None:
            print(">>> No existing " + server_name + " server found, creating...")
            server = conn.compute.create_server(
                name=server_name,
                image_id=image.id,
                flavor_id=flavour.id,
                networks=[{"uuid": network.id}],
                key_name=keypair.name,
                security_groups=[security_group])
            print(">>> Waiting for " + server_name + " server creation, this may take some time...")
            server = conn.compute.wait_for_server(server)
            print(server_name + " server created, continuing...")
        else:
            print(">>> Existing " + server_name + " server found, continuing...")

# PUBLIC NETWORK: Check for public network and panic if not present
    print(">>> Checking for public network...")
    public_net = conn.network.find_network(name_or_id='public-net')
    if public_net:
        print(">>> Found public network...")
        avail_ip = conn.network.find_available_ip()
    else:
        print("Shitbags, that didn't work!")

# EXTERNAL NET DICT: Create external network dict info for use upon router creation
    network_dict_body = {
            'network_id': public_net.id
            }
# ROUTER: Check for router and create if not present
    print(">>> Checking for existing router...")
    router = conn.network.find_router(name_or_id='parkelj1-rtr')
    if router:
        print('>>> Existing router detected, continuing...')
    else:
        print('>>> Creating router "parkelj1-rtr"')
        router = conn.network.create_router(name='parkelj1-rtr', external_gateway_info=network_dict_body)

#   MAYBE MOVE THE FLOATING IP STUFF TO HERE AND DELETE THE ROUTER AND RECREATE IT WITH FLOATING IP IF ROUTER EXISTS
#   I WOULD NEED TO REMOVE THE "else" STATEMENT ABOVE AND JUST RUN THE CREATE ROUTER AS OF RIGHT.
#
# INTERFACE: Add interface to router
    conn.network.add_interface_to_router(router,subnet.id)

# FLOATING IP: Check for existing/available floating IP and add if it doesn't exist
    print("Checking for existing IP:")
    for ip in conn.network.ips(**{'floating_network_id' : public_net.id, 'router_id' : router.id}):
        floating_ip = ip

    if floating_ip is None:
        print(" > Unable to find an available IP, creating...")
        floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
        conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)
    
    print(floating_ip.floating_ip_address)
    
#    print(">>> Attempting to add floating IP...")
#    if avail_ip:
#        print("Available IP:")
#        print(avail_ip.floating_ip_address)
#        floating_ip = avail_ip;
#    else:
#        print(">>> Unable to find available IP, creating...")
#        floating_ip = conn.network.create_ip(floating_network_id=public_net.id)

# Add floating IP to server
#    conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)

# CREATE: Now lets call our function
create(conn)
print(">>> FINISHED CREATE FUNCTION, NOW MOVING TO RUN FUNCTION...")

def run(conn):
    all_server_names = []
    my_server_names = ['parkelj1-app','parkelj1-db','parkelj1-web']

#   SERVER: Check for servers and alert if not present
    for server in conn.compute.servers():

    #   Build array of all server names from the generator
        all_server_names.append(server.name)

        if server.name in my_server_names:
            print(">>> Checking for existing " + server.name + " server...")
            print("  > Found server " + server.name + "...")
            print("  > " + server.name + " has a status of: '" + server.status + "'")
            if server.status != 'ACTIVE':
                conn.compute.start_server(server)
                conn.compute.wait_for_server(server,status='ACTIVE')
                print("  > " + server.name + " is now '" + server.status + "'")
            else:
                print("  > " + server.name + " is already 'ACTIVE'.")
            print()

#   Check that all servers are there
    for server_name in my_server_names:
        if server_name not in all_server_names:
            print(">>> Checking for existing " + server_name + " server...")
            print("  > Unable to find server: " + server_name + ", please create the server first...\n")

# RUN: Now lets call our function
run(conn)

print(">>> FINISHED RUN  FUNCTION, NOW MOVING TO STOP FUNCTION...")


def stop(conn):
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    all_server_names = []
    my_server_names = ['parkelj1-app','parkelj1-db','parkelj1-web']

#   SERVER: Check for servers and alert if not present
    for server in conn.compute.servers():

#   Build array of all server names from the generator
        all_server_names.append(server.name)

        if server.name in my_server_names:
            print(">>> Checking for existing " + server.name + " server...")
            print("  > Found server " + server.name + "...")
            if server.status == 'ACTIVE':
                print("  > " + server.name + " has a status of '" + server.status + "', shutting off...")
                conn.compute.stop_server(server)
                conn.compute.wait_for_server(server,status='SHUTOFF')
                print("  > " + server.name + " is now '" + server.status + "'")
            else:
                print("  > " + server.name + " is not active.")
            print()

#   Check that the servers are all there
    for server_name in my_server_names:
        if server_name not in all_server_names:
            print(">>> Checking for existing " + server_name + " server...")
            print("  > " + server_name + " does not appear to exist... so ahh, yeah...")
            print()

#   RUN: Now lets call our function
run(conn)
print(">>> FINISHED STOP FUNCTION, NOW MOVING TO DESTROY FUNCTION...")


def destroy(conn):
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    all_server_names = []
    my_server_names = ['parkelj1-app','parkelj1-db','parkelj1-web']
    floating_ip = False
    server_with_floating_ip = False

#   SERVER: Check for servers and alert if not present
    for server in conn.compute.servers():

    #   Build array of all server names from the generator
        all_server_names.append(server.name)

        if server.name in my_server_names:
#            metadata = conn.compute.get_server_metadata(server)
#            for metadatum in metadata:
#                print(server[metadatum])
            for address_data in server['addresses']['parkelj1-net']:
                for address_datum in address_data:
                    if address_data['OS-EXT-IPS:type'] == 'floating':
                    #   Remove floating IP from server
                        floating_ip = address_data['addr']
                        server_with_floating_ip = server
#   FLOATING IP: Check if we have a floating IP and delete it from the appropriate server
    if floating_ip and server_with_floating_ip:
        print(floating_ip)
        conn.compute.remove_floating_ip_from_server(server_with_floating_ip, floating_ip)
        conn.network.delete_ip(conn.network.find_ip(name_or_id=floating_ip))

#   ROUTER: Find our router
    router = conn.network.find_router(name_or_id='parkelj1-rtr')

#   NETWORK: Find our network and delete it
    print(">>> Locating and deleting network: 'osbots1-net'...")
    for network in conn.network.networks(**{'name':'parkelj1-net'}):
        print(network)
        for subnet in network.subnet_ids:
            conn.network.remove_interface_from_router(router,subnet)
            ports = conn.network.get_subnet_ports(subnet)
            for port in ports:
                conn.network.delete_port(port)
            conn.network.delete_subnet(conn.network.get_subnet(subnet))
    #   Now delete the network(s)
        conn.network.delete_network(network)
        print("  > Network deleted")

    for router in conn.network.routers(**{'name':'parkelj1-rtr'}):
        for routes in router['routes']:
            print(routes)
        print(router['routes'])
    print(">>> Locating and deleting router: 'parkelj1-rtr'...")
    router = conn.network.find_router(name_or_id='parkelj1-rtr')
    if router:
        conn.network.delete_router(router)
    print("  > Router deleted")

#   SERVER: delete our servers
    print(">>> Locating and deleting servers...")
    for server in my_server_names:
        conn.compute.delete_server(conn.compute.find_server(server))
        print(server + " server has been deleted.")

# DESTROY: Now lets call our function
destroy(conn)


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
