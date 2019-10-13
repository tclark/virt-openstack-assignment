import openstack

# After we have done our imports we need to instantiate a connection.
conn = openstack.connect(cloud_name='openstack')

# Our destroy() function will remove all the resources for our servers
def destroy(conn):
    
    my_server_names = ['osbots1-app','osbots1-db','osbots1-web']
    my_active_server_names = []
    floating_ip = False
    server_with_floating_ip = False

    print("Preparing to destroy servers...")
#   SERVER: Check for servers and alert if not present
    for server in conn.compute.servers():
        if server.name in my_server_names:
#           Build array of all server names from the generator
            my_active_server_names.append(server.name)
            if server['addresses']:
                if server['addresses']['osbots1-net']:
                    for address_data in server['addresses']['osbots1-net']:
                        for address_datum in address_data:
                            if address_data['OS-EXT-IPS:type'] == 'floating':
#                               Remove floating IP from server
                                floating_ip = address_data['addr']
                                server_with_floating_ip = server

#   FLOATING IP: Check if we have a floating IP and delete it from the appropriate server
    if floating_ip and server_with_floating_ip:
        print(" > Found floating IP '" + floating_ip + "', removing...")
        conn.compute.remove_floating_ip_from_server(server_with_floating_ip, floating_ip)
        conn.network.delete_ip(conn.network.find_ip(name_or_id=floating_ip))
        print("  > Floating IP removed.")

#   ROUTER: Find our router
    router = conn.network.find_router(name_or_id='osbots1-rtr')

#   NETWORK: Find our network and delete it
    print(" > Searching for network 'osbots1-net'...")
    for network in conn.network.networks(**{'name':'osbots1-net'}):
        for subnet in network.subnet_ids:
            conn.network.remove_interface_from_router(router,subnet)
            ports = conn.network.get_subnet_ports(subnet)
            for port in ports:
                conn.network.delete_port(port)
            conn.network.delete_subnet(conn.network.get_subnet(subnet))
#       Now delete the network(s) 
        conn.network.delete_network(network)
        print("  > Network 'osbots1-net' deleted")
    if network is None:
        print("  > No network found.")

#   ROUTER: now remove our router
    print(" > Searching for router 'osbots1-rtr'...")
    router = conn.network.find_router(name_or_id='osbots1-rtr')
    if router:
        conn.network.delete_router(router)
        print("  > Router 'osbots1-rtr' deleted")
    else:
        print("  > No router found.")

#   SERVER: delete our servers
    print(" > Searching for servers...")
    if my_active_server_names:
        for server in my_active_server_names:
            conn.compute.delete_server(conn.compute.find_server(server))
            print("  > Server '" + server + "' has been deleted.")
    else:
        print("  > No active servers found, finished.")

# DESTROY: Now lets call our function
destroy(conn)

