import openstack

# After we have done our imports we need to instantiate a connection.
conn = openstack.connect(cloud_name='openstack')

# Our status() function will show the current status of our servers
def status(conn):

    all_server_names = []
    my_server_names = ['parkelj1-app','parkelj1-db','parkelj1-web']
    floating_ip = False
    server_with_floating_ip = False

#   SERVER: Check for servers and alert if they aren't present
    for server in conn.compute.servers():

    #   Build an array of all server names from the generator
        all_server_names.append(server.name)

        # If the servers are present, print the status of each server
        if server.name in my_server_names:
            print("Server information for: " + server.name)
            print(" > Status: " + server.status)

            #print the fixed and floating (if present) IP addresses of each server
            for address_data in server['addresses']['parkelj1-net']:
                #for address_datum in address_data:
                    if address_data['OS-EXT-IPS:type'] == 'fixed':
                        print(" > Fixed IP: " + address_data['addr'])
                    if address_data['OS-EXT-IPS:type'] == 'floating':
                        print(" > Floating IP: " + address_data['addr'])
    else:
        print("No existing network or servers found")

# STATUS: Now lets call our function
status(conn)

