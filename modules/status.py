import openstack

# After we have done our imports we need to instantiate a connection.
conn = openstack.connect(cloud_name='openstack')

# Our status() function will show the current status of our servers
def status(conn):
    
    all_server_names = []
    my_server_names = ['osbots1-app','osbots1-db','osbots1-web']
    floating_ip = False
    server_with_floating_ip = False

#   SERVER: Check for servers and alert if not present
    for server in conn.compute.servers():

    #   Build array of all server names from the generator
        all_server_names.append(server.name)

        if server.name in my_server_names:
            print("Server information for: " + server.name)
            print(" > Status: " + server.status)

            for address_data in server['addresses']['osbots1-net']:
                #for address_datum in address_data:
                    if address_data['OS-EXT-IPS:type'] == 'fixed':
                        print(" > Fixed IP: " + address_data['addr'])
                    if address_data['OS-EXT-IPS:type'] == 'floating':
                        print(" > Floating IP: " + address_data['addr'])

# STATUS: Now lets call our function
status(conn)

