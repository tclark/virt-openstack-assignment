# Adapted from examples on the openstack github https://github.com/openstack/openstacksdk/tree/master/examples/compute

#

from configparser import SectionProxy
from unicodedata import name
import constant
import argparse
import openstack

conn = openstack.connect(cloud_name='openstack', region_name='nz-por-1')

# checking for existing networks
def getNetwork():
    network = conn.network.find_network(constant.NETWORK)
    return network

def getSubnet():
    subnet = conn.network.find_subnet(constant.SUBNET)
    return subnet

def getRouter():
    router = conn.network.find_router(constant.ROUTERNAME)
    return router

def get_floating_ip():
    ''' Get a floating IP address from the pool
    '''
    floating_ip = conn.network.create_ip(floating_network_id=conn.network.find_network("public-net").id)
    return floating_ip

def create_network():
    print("Checking network status...")

    # define network variables
    network = getNetwork()
    subnet = getSubnet()
    router = getRouter()

    # check for network and create if non existing
    if (network is None):
        network = conn.network.create_network(
            name=constant.NETWORK
        )
        print("Created network with name " + constant.NETWORK)

    # check for subnet and create if non existing
    if (subnet is None):
        subnet = conn.network.create_subnet(
            name=constant.SUBNET,
            network_id=network.id,
            ip_version='4',
            cidr=constant.CIDR,
            gateway_ip=constant.GATEWAY_IP
        )
        print("Created subnet with name " + constant.SUBNET)

    # Check for router and create if non existing
    if (router is None):
        try:
            router = conn.network.create_router(
                name="westcl4-net",
                external_gateway_info={"network_id": conn.network.find_network("public-net").id})
            print("Created router with attributes: ")
        except:
            print("Router creation failed")
        router = conn.network.add_interface_to_router(
            router, 
            subnet_id=subnet.id)
        print(router)
    else:
        print("Router already exists")

    print(floating_ip)
    # Check for floating IP and create if non existing
    if (floating_ip is None):
        floating_ip = conn.network.create_ip(
            floating_network_id=conn.network.find_network("public-net").id)
        print("Created floating IP with attributes: ")
        print(floating_ip)

def get_current_servers():
    servers = {
        f'westcl4-web': conn.compute.find_server(f'westcl4-web', ignore_missing=True),
        f'westcl4-app': conn.compute.find_server(f'westcl4-app', ignore_missing=True),
        f'westcl4-db': conn.compute.find_server(f'westcl4-db', ignore_missing=True)
    }
    return servers

# checking for existing compute
def get_app():
    app = conn.compute.get_server('westcl4-app')
    return app

def get_web():
    web = conn.compute.get_server(constant.WEB_NAME)
    return web

def get_db():
    db = conn.compute.get_server(constant.DB_NAME)
    return db


def create_compute():
    print("Checking compute status...")
    print("Note: Each server instance will take a few minutes to create.")
    # define compute variables
    app = get_app()
    web = get_web()
    db = get_db()
    
    public = conn.network.find_network(constant.PUBLIC_NET).id


    # check for app server and create if non existing
    if (app is None):
        def create_app():
            print("Creating app server with attributes: ")
            app = conn.compute.create_server(
                name=constant.APP_NAME,
                image_id=conn.compute.find_image(constant.IMAGE).id,
                flavor_id=conn.compute.find_flavor(constant.FLAVOUR).id,
                networks=[
                    {"uuid": conn.network.find_network(constant.NETWORK).id}],
            )
            app = conn.compute.wait_for_server(app)
            conn.compute.add_security_group_to_server(app, constant.SECURITY_GROUP)
            print(app)
        create_app()

    # check for web server and create if non existing
    if (web is None):
        def create_web():
            print("Creating web server with attributes: ")
            web = conn.compute.create_server(
                name=constant.WEB_NAME,
                image_id=conn.compute.find_image(constant.IMAGE).id,
                flavor_id=conn.compute.find_flavor(constant.FLAVOUR).id,
                networks=[
                    {"uuid": conn.network.find_network(constant.NETWORK).id}]
            )
            web = conn.compute.wait_for_server(web)
            conn.compute.add_security_group_to_server(app, constant.SECURITY_GROUP)
            ip = conn.network.create_ip(floating_network_id=public)
            conn.compute.add_floating_ip_to_server(app, ip.floating_ip_address)
            print(web)
        create_web()

    # check for db server and create if non existing
    if (db is None):
        def create_db():
            print("Creating db server with attributes: ")
            db = conn.compute.create_server(
                name=constant.DB_NAME,
                image_id=conn.compute.find_image(constant.IMAGE).id,
                flavor_id=conn.compute.find_flavor(constant.FLAVOUR).id,
                networks=[
                    {"uuid": conn.network.find_network(constant.NETWORK).id}]
            )
            db = conn.compute.wait_for_server(db)
            conn.compute.add_security_group_to_server(app, constant.SECURITY_GROUP)
            print(db)
        create_db()
    return


def run_compute():
    ''' Start the compute resources created by the create action '''
    print("Starting compute resources...")

    #create array and populate with servers
    servers = get_current_servers()
    for server_name, server in servers.items():
        if(server is not None):
            res = conn.compute.get_server(server.id)
            if(res.status == "SHUTOFF"):
                print("Starting server:  {} ".format(server_name))
                conn.compute.start_server(server.id)
            else:
                print("Server already running:  {} ".format(server_name))
        else:
            print("Server unavailable:  {} ".format(server_name))  

def stop_compute():
    ''' Stop the compute resources created by the create action '''
    print("Stopping compute resources...")

    servers = get_current_servers()
    for server_name, server in servers.items():
        if(server is not None):
            res = conn.compute.get_server(server.id)
            if(res.status == "ACTIVE"):
                print("Stopping server: {} ".format(server_name))
                conn.compute.stop_server(server.id)
            else:
                print("Server already stopped: {} ".format(server_name))
        else:
            print("Server unavailable: {} ".format(server_name))
    
def get_status():
    #get server status and print to terminal
    servers = get_current_servers()
    for server_name, server in servers.items():
        if(server is not None):
            res = conn.compute.get_server(server.id)
            print("Server: {} Status: {} ".format(server_name, res.status))
        else:
            print("Server unavailable: {} ".format(server_name))
    pass 

def create():
    ''' Create a set of Openstack resources '''
    print("Creating resources...")
    create_network()
    create_compute()
    pass


def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    run_compute()
    pass


def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    stop_compute()
    pass


def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    pass


def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    get_status()
    pass


### You should not modify anything below this line ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation',
                        help='One of "create", "run", "stop", "destroy", or "status"')
    args = parser.parse_args()
    operation = args.operation

    operations = {
        'create': create,
        'run': run,
        'stop': stop,
        'destroy': destroy,
        'status': status
    }

    action = operations.get(operation, lambda: print(
        '{}: no such operation'.format(operation)))
    action()
