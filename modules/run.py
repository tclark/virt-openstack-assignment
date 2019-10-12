import argparse
import openstack
conn = openstack.connect(cloud_name='openstack')


def run(conn):
    all_server_names = []
    my_server_names = ['parkelj1-app','parkelj1-db','parkelj1-web']

#   SERVER: Check for servers and alert if they're present
    for server in conn.compute.servers():

    #   Build an array of all server names from the generator
        all_server_names.append(server.name)

        #Check if the server is there and print that it's found it then print it's status
        if server.name in my_server_names:
            print(">>> Checking for existing " + server.name + " server...")
            print("  > Found server " + server.name + "...")
            print("  > " + server.name + " has a status of: '" + server.status + "'")
            # If the server isn't active, start it and then print the status
            if server.status != 'ACTIVE':
                conn.compute.start_server(server)
                conn.compute.wait_for_server(server,status='ACTIVE')
                print("  > " + server.name + " is now '" + server.status + "'")
            else:
                print("  > " + server.name + " is already 'ACTIVE'.")
            print()

#   Check that all the servers are there
    for server_name in my_server_names:
        if server_name not in all_server_names:
            print(">>> Checking for existing " + server_name + " server...")
            print("  > Unable to find server: " + server_name + ", please create the server first...\n")

# RUN: Now lets call our function
run(conn)

