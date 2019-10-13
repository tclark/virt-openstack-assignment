import argparse
import openstack

conn = openstack.connect(cloud_name='openstack')
IMAGE = "ubuntu-minimal-16.04-x86_64"
FLAVOR = "c1.c1r1"
KEYPAIR = "mcinrl1-key"
NETWORK = "mcinrl1-net"
SUBNET = "mcinrl1-subnet"
names = ["mcinrl1-web", "mcinrl1-app", "mcinrl1-db"]


def create():
    'Create a set of Openstack resources'
    
    network = conn.network.find_network(NETWORK)
    if network is None:
        network = conn.network.create_network(NETWORK)
        subnet = conn.network.create_subnet(
            name=SUBNET,
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24',
            gateway_ip='192.168.50.1')

    floating_ip = conn.network.create_ip(floating_network_id=conn.network.find_network('public-net').id)

    image = conn.compute.find_image(IMAGE)
    flavor = conn.compute.find_flavor(FLAVOR)
    
    for name in names:
        server = conn.compute.create_server(name=name, image_id=image.id, flavor_id=flavor.id,networks=[{"uuid": network.id}])
        server = conn.compute.wait_for_server(server)

def run():
    ' Start a set of Openstack virtual machines if they are not already running.'
    for name in names:
        server = conn.compute.find_server(name)
        if server is None:
            print(server.name +" does not exist")
        else:
            if server.STATUS == "ACTIVE":
                print(server.name+" is already running")
            else: 
                conn.compute.start_server(server)


def stop():
    'Stop a set of Openstack virtual machines if they are running.'
    for name in names:
        for server in conn.compute.servers():
            if server.name == name:
                if server.status = "ACTIVE":
                    conn.compute.stop_server(server)
                    print(server.name + " was stopped")
                else:
                    print(server.name+" is already stopped")

def destroy():
    'Tear down the set of Openstack resources produced by the create action'
    
    network = conn.network.find_network(NETWORK)
    if network is None
        print("No network to delete")
    else:
        for subnet in network.subnet_ids:
            conn.network.delete_subnet(subnet, ignore_missing=False)
        conn.network.delete_network(network, ignore_missing=False)

    for name in names:
        server = conn.compute.find_server(name)
        if server is None:
            print(server.name + " is already deleted or was never created")
        else:
            conn.compute.delete_server(server)


def status():
    'Print a status report on the OpenStack virtual machines created by the create action.'

    for name in names:
        server = conn.compute.find_server(name)
        if server is None:
            print(server.name+" does not exist")
        else:
            print("Name: "+server.name)
            print("Status: "+server.status)


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
