import argparse
import openstack
import time

# Connect to openstack
conn = openstack.connect(cloud_name="openstack")
# Server names to check for
serverList = ["caincb1-web", "caincb1-app", "caincb1-db"]

# Server information
IMAGE = "ubuntu-minimal-16.04-x86_64"
FLAVOUR = "c1.c1r1"
NETWORK = "caincb1-net"
SECURITY_GROUP = "assignment2"
SUBNET = "caincb1-subnet"
ROUTER = "caincb1-rtr"
KEYPAIR = "caincb1-key"

image = conn.compute.find_image(IMAGE)
flavour = conn.compute.find_flavor(FLAVOUR)
keypair = conn.compute.find_keypair(KEYPAIR)


def create():
    ''' Create a set of Openstack resources '''

    # Create network if not already existing.
    network = conn.network.find_network(NETWORK)
    if network is None:
        print("Attempting to create network \"{}\"".format(NETWORK))
        network = conn.network.create_network(name=NETWORK)
        # Create subnet for network.
        subnet = conn.network.create_subnet(name=SUBNET,
            network_id=network.id,
            ip_version=4,
            cidr="192.168.50.0/24",
            gateway_ip="192.168.50.1")
        print("Network \"{}\" has been created successfully.".format(NETWORK))

    # Create router if not already existing.
    router = conn.network.find_router(ROUTER, ignore_missing=True)
    if router is None:
        print("Attempting to create router \"{}\"".format(ROUTER))
        attrs = {"name" : ROUTER, "external_gateway_info" : {"network_id" : conn.network.find_network("public-net").id}}
        router = conn.network.create_router(**attrs)
        conn.network.add_interface_to_router(router, subnet_id=conn.network.find_network(NETWORK).subnet_ids[0])
        print("Router \"{}\" has been created successfully.".format(ROUTER))

    # Create servers from list.
    for name in serverList:
        print("Attempting to create server \"{}\"".format(name))
        server = conn.compute.find_server(name)
        if server is None:
            server = conn.compute.wait_for_server(conn.compute.create_server(name=name,
                image_id=image.id,
                flavor_id=flavour.id,
                networks=[{"uuid": network.id}],
                key_name=keypair.name,
                security_groups=[{"name": SECURITY_GROUP}]))
            # Create and add floating ip to web server.
            if name == "caincb1-web":
                floating_ip = conn.network.create_ip(floating_network_id=conn.network.find_network('public-net').id)
                conn.compute.add_floating_ip_to_server(server, address=floating_ip.floating_ip_address)
            print("Server \"{}\" was created succesfully.".format(name))
        else:
            print("ERROR! Server \"{}\" has already been created.".format(name))


def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''

    for name in serverList:
        print("Attempting to start server \"{}\"".format(name))
        server = conn.compute.find_server(name)
        if server is None:
            print("ERROR! Server \"{}\" was not found and can not be started.".format(name))
        else:
            if conn.compute.get_server(server).status != "ACTIVE":
                conn.compute.start_server(server)
                print("Server \"{}\" has been started successfully.".format(name))
            else:
                print("Server \"{}\" is already active therefore the state has not been changed.".format(name))


def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''

    for name in serverList:
        print("Attempting to stop server \"{}\"".format(name))
        server = conn.compute.find_server(name)
        if server is None:
            print("ERROR! Server \"{}\" was not found and can not be stopped.".format(name))
        else:
            if conn.compute.get_server(server).status == "ACTIVE":
                conn.compute.stop_server(server)
                print("Server \"{}\" has been stopped successfully.".format(name))
            else:
                print("Server \"{}\" is not active therefore the state has not been changed.".format(name))


def destroy():
    ''' Tear down the set of Openstack resources
    produced by the create action
    '''

    for name in serverList:
        server = conn.compute.find_server(name)
        if server is not None:
            print("Attempting to destroy server \"{}\"".format(name))
            if name == "caincb1-web":
                # Finds floating ip address of web server and deletes it before deleting the server itself.
                conn.network.delete_ip(conn.network.find_ip(conn.compute.get_server(server).addresses[NETWORK][1]["addr"]))
            conn.compute.delete_server(server)
            print("Server \"{}\" was successfully destroyed.".format(name))
    router = conn.network.find_router(ROUTER, ignore_missing=True)
    if router is not None:
        print("Attempting to destroy router \"{}\"".format(ROUTER))
        conn.network.remove_interface_from_router(router, conn.network.find_network(NETWORK, ignore_missing=True).subnet_ids[0])
        conn.network.delete_router(router)
        print("Router \"{}\" has successfully been destroyed.".format(ROUTER))
    network = conn.network.find_network(NETWORK, ignore_missing=True)
    if network is not None:
        print("Attempting to destroy network \"{}\"".format(NETWORK))
        # Wait for the servers to be deleted before attempting to delete the network to prevent errors.
        time.sleep(3)
        conn.network.delete_network(network)
        print("Network \"{}\" has successfully been destroyed.".format(NETWORK))


def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''

    for name in serverList:
         server = conn.compute.find_server(name)
         if server is None:
             print("ERROR! Server \"{}\" was not found.".format(name))
         else:
             server = conn.compute.get_server(server)
             ip_address = server.addresses[NETWORK][0]["addr"]
             if ip_address is None:
                 ip_address = "N/A"
             print("======={}=======".format(name))
             print("status: {}".format(server.status))
             print("ip address: {}\n".format(ip_address))


### You should not modify anything below this line ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation',
                        help='One of "create", "run", "stop", "destroy", or "status"')
    args = parser.parse_args()
    operation = args.operation

    operations = {
        'create'  : create,
        'run'     : run,
        'stop'    : stop,
        'destroy' : destroy,
        'status'  : status
        }

    action = operations.get(operation, lambda: print('{}: no such operation'.format(operation)))
    action()
