import argparse
import openstack

# After we have done our imports we need to instantiate a connection.
conn = openstack.connect(cloud_name='openstack')

# Our destroy() function will remove all the resources for our servers
def destroy(conn):
    
    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    all_server_names = []
    my_server_names = ['osbots1-app','osbots1-db','osbots1-web']
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
            for address_data in server['addresses']['osbots1-net']:
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
    router = conn.network.find_router(name_or_id='osbots1-rtr')

#   NETWORK: Find our network and delete it
    print(">>> Locating and deleting network: 'osbots1-net'...")
    for network in conn.network.networks(**{'name':'osbots1-net'}):
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
                            
    for router in conn.network.routers(**{'name':'osbots1-rtr'}):
        for routes in router['routes']:
            print(routes)
        print(router['routes'])
    print(">>> Locating and deleting router: 'osbots1-rtr'...")
    router = conn.network.find_router(name_or_id='osbots1-rtr')
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

