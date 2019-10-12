import argparse
import openstack
conn = openstack.connect(cloud_name='openstack')

def stop(conn):

    all_server_names = []
    my_server_names = ['parkelj1-app','parkelj1-db','parkelj1-web']

#   SERVER: Check for all servers and alert if they're not present
    for server in conn.compute.servers():

#   Build array of all server names from the generator
        all_server_names.append(server.name)
        
        # If the server is found, print that it's been found
        if server.name in my_server_names:
            print(">>> Checking for existing " + server.name + " server...")
            print("  > Found server " + server.name + "...")
            # If the server is active, shut it off
            if server.status == 'ACTIVE':
                print("  > " + server.name + " has a status of '" + server.status + "', shutting off...")
                conn.compute.stop_server(server)
                conn.compute.wait_for_server(server,status='SHUTOFF')
                print("  > " + server.name + " is now '" + server.status + "'")
            else: #if server has already been shut off, print that it isn't active
                print("  > " + server.name + " is not active.")
            print()

#   Check that the servers are all there
    for server_name in my_server_names:
        if server_name not in all_server_names:
            print(">>> Checking for existing " + server_name + " server...")
            print("  > " + server_name + " does not exist")
            print()

#   RUN: Now lets call our function
stop(conn)

