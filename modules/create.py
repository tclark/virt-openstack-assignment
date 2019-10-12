import argparse
import openstack
conn = openstack.connect(cloud_name='openstack')

def create(conn):

    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'
    KEYPAIR = 'parkelj1-key'

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    server_names = ['parkelj1-app','parkelj1-db','parkelj1-web']
    floating_ip =  None

# NETWORK: Check for a network and create it if its not there
    print(">>> Checking for existing networks...")
    network = conn.network.find_network('parkelj1-net')
    if network is None:
        print(">>> No existing network found, please wait...")
        network = conn.network.create_network(name='parkelj1-net')
    else:
        print(">>> Existing network found")

# SECURITY GROUP: Check for security group, so it can be used when the server is created
    print(">>> Checking for the security group 'assignment2'...")
    security_group = conn.network.find_security_group(name_or_id='assignment2')
    if security_group is None:
        print(">>> Unable to find the 'assignment2' security group...")

# SUBNET: Check for subnet and create it if it's not present
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
        print(">>> Subnet exists.")


# SERVER: Check for servers (array) and create them if they're  not present
    for server_name in server_names:
        print(">>> Checking for existing " + server_name + " server...")
        server = conn.compute.find_server(server_name)
        if server is None:
            print(">>> No existing " + server_name + " server found, please wait...")
            server = conn.compute.create_server(
                name=server_name,
                image_id=image.id,
                flavor_id=flavour.id,
                networks=[{"uuid": network.id}],
                key_name=keypair.name,
                security_groups=[security_group])
            print(">>> Waiting for " + server_name + " server to be created, this might take a while...")
            server = conn.compute.wait_for_server(server)
            print(server_name + " server created, continuing...")
        else:
            print(">>> Existing " + server_name + " server found...")

# PUBLIC NETWORK: Check for public network and print an error message if its not present
    print(">>> Checking for public network...")
    public_net = conn.network.find_network(name_or_id='public-net')
    if public_net:
        print(">>> Public network found...")
    else:
        print("Public network NOT found...")

# EXTERNAL NET DICT: Create external network dict info for use when router is created
    network_dict_body = {
            'network_id': public_net.id
            }
# ROUTER: Check for router and create if it's not present
    print(">>> Checking for existing router...")
    router = conn.network.find_router(name_or_id='parkelj1-rtr')
    if router:
        print('>>> Existing router detected, continuing...')
    else:
        print('>>> Creating router "parkelj1-rtr"')
        router = conn.network.create_router(name='parkelj1-rtr', external_gateway_info=network_dict_body)


# INTERFACE: Add interface to router
    conn.network.add_interface_to_router(router,subnet.id)

# FLOATING IP: Check for existing/available floating IP and add if it doesn't exist
    print("Checking for existing IP:")
    for ip in conn.network.ips(**{'floating_network_id': public_net.id, 'router_id': router.id}):
        floating_ip = ip

    if floating_ip is None:
        print(" > Unable to find an available IP, please wait while it's created...")
        floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
        conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)

    print("Your floating IP address is: " + floating_ip.floating_ip_address)

# CREATE: Now lets call our function
create(conn)

