import argparse
import openstack
conn = openstack.connect(cloud_name='openstack')


def destroy(conn):

    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    all_server_names = []
    my_server_names = ['parkelj1-app','parkelj1-db','parkelj1-web']
    floating_ip = False
    server_with_floating_ip = False

#   SERVER: Check to see if all servers exist and alert if they don't
    for server in conn.compute.servers():

    #   Build array of all server names from the generator
        all_server_names.append(server.name)

        if server.name in my_server_names:

            for address_data in server['addresses']['parkelj1-net']:
                for address_datum in address_data:
                    # If the metadata OS-EXT-IP type is floating, set it as the floating_IP then you can use it to remove it later
                    if address_data['OS-EXT-IPS:type'] == 'floating':
                        floating_ip = address_data['addr']
                        server_with_floating_ip = server
#   FLOATING IP: Check if there's a floating IP and delete it from the appropriate server
    if floating_ip and server_with_floating_ip:
#        print(floating_ip)
        conn.compute.remove_floating_ip_from_server(server_with_floating_ip, floating_ip)
        conn.network.delete_ip(conn.network.find_ip(name_or_id=floating_ip))

#   ROUTER: Find the router
    router = conn.network.find_router(name_or_id='parkelj1-rtr')

#   NETWORK: Find the network and delete it
    print(">>> Locating and deleting network: 'parkelj1-net'...")
    for network in conn.network.networks(**{'name':'parkelj1-net'}):
#        print(network)
        # Find the subnet and ports and remove from the router, otherwise you can't delete the router
        for subnet in network.subnet_ids:
            conn.network.remove_interface_from_router(router,subnet)
            ports = conn.network.get_subnet_ports(subnet)
            for port in ports:
                conn.network.delete_port(port)
            conn.network.delete_subnet(conn.network.get_subnet(subnet))
    #   Now delete the network(s)
        conn.network.delete_network(network)
        print("  > Network deleted")

    # Find the router and delete it
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

