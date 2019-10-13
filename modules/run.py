import argparse
import openstack

# After we have done our imports we need to instantiate a connection.
conn = openstack.connect(cloud_name='openstack')

# Our create() function will create a network, router, subnet and server
def run(conn):

    all_server_names = []
    my_server_names = ['osbots1-app','osbots1-db','osbots1-web']

#   SERVER: Check for servers and alert if not present
    for server in conn.compute.servers():

    #   Build array of all server names from the generator
        all_server_names.append(server.name)

        if server.name in my_server_names:
            print("Checking for existing " + server.name + " server...")
            print(" > Found server " + server.name + "...")
            print(" > " + server.name + " has a status of: '" + server.status + "'")
            if server.status != 'ACTIVE':
                conn.compute.start_server(server)
                conn.compute.wait_for_server(server,status='ACTIVE')
                print(" > " + server.name + " is now '" + server.status + "'")
            else:
                print(" > " + server.name + " is already 'ACTIVE'.")
            print()

#   Check that my servers are all here
    for server_name in my_server_names:
        if server_name not in all_server_names:
            print("Checking for existing " + server_name + " server...")
            print(" > Unable to find server: " + server_name + ", please create the server first...\n")

# RUN: Now lets call our function
run(conn)

