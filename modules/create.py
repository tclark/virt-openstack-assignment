import openstack

# After we have done our imports we need to instantiate a connection.
conn = openstack.connect(cloud_name='openstack')

# Our create() function will create a network, router, subnet and server
def create(conn):
    
    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'
    KEYPAIR = 'osbots1'

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)
    server_names = ['osbots1-app','osbots1-db','osbots1-web']
    floating_ip = None

# NETWORK: Check for network and create if not present
    print("Checking for existing networks:")
    network = conn.network.find_network('osbots1-net')
    if network is None:
        print(" > No existing network found, creating...")
        network = conn.network.create_network(name='osbots1-net')
    else:
        print(" > Existing network found, continuing...")

# SECURITY GROUP: Check for security group, so we can use upon server creation
    print("Checking for security group 'assignment2':")
    security_group = conn.network.find_security_group(name_or_id='assignment2')
    if security_group is None:
        print(" > Unable to find preferred security group, continuing...")

# SUBNET: Check for subnet and create if not present
    print("Checking for existing subnets:")
    subnet = conn.network.find_subnet('osbots1-subnet')
    if subnet is None:
        print(" > Creating subnet...")
        subnet = conn.network.create_subnet(
            name='osbots1-subnet',
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1')
    else:
        print(" > Subnet exists, continuing...")

# SERVER: Check for web server and create if not present
    for server_name in server_names:
        print("Checking for existing " + server_name + " server:")
        server = conn.compute.find_server(server_name)
        if server is None:
            print(" > No existing " + server_name + " server found, creating...")
            server = conn.compute.create_server(
                name=server_name,
                image_id=image.id,
                flavor_id=flavour.id,
                networks=[{"uuid": network.id}],
                key_name=keypair.name,
                security_groups=[security_group])
            print(" > Waiting for " + server_name + " server creation, this may take some time...")
            server = conn.compute.wait_for_server(server)
            print(" > " + server_name + " server created, continuing...")
        else:
            print(" > Existing " + server_name + " server found, continuing...")

# PUBLIC NETWORK: Check for public network and panic if not present
    print("Checking for public network:")
    public_net = conn.network.find_network(name_or_id='public-net')
    if public_net:
        print(" > Found public network...")
    else:
        print(" > Shitbags, that didn't work!")

# EXTERNAL NET DICT: Create external network dict info for use upon router creation
    network_dict_body = {
            'network_id': public_net.id
            }
# ROUTER: Check for router and create if not present
    print("Checking for existing router:")
    router = conn.network.find_router(name_or_id='osbots1-rtr')
    if router:
        print(' > Existing router detected, continuing...')
    else:
        print(' > Creating router "osbots1-rtr"')
        router = conn.network.create_router(name='osbots1-rtr', external_gateway_info=network_dict_body)
#
#   MAYBE MOVE THE FLOATING IP STUFF TO HERE AND DELETE THE ROUTER AND RECREATE IT WITH FLOATING IP IF ROUTER EXISTS
#   I WOULD NEED TO REMOVE THE "else" STATEMENT ABOVE AND JUST RUN THE CREATE ROUTER AS OF RIGHT.
#

# INTERFACE: Add interface to router   
    conn.network.add_interface_to_router(router,subnet.id)

#   FLOATING IP: Check for floating IP and add if required
    print("Checking for existing floating IP:")
    for ip in conn.network.ips(**{'floating_network_id': public_net.id, 'router_id': router.id}):
        floating_ip = ip
    
    if floating_ip is None:
        print(" > Unable to find available IP, creating...")
        floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
        conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)

    print(" > Floating IP '" + floating_ip.floating_ip_address + "' added.")

# CREATE: Now lets call our function
create(conn)

