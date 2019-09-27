import argparse
import openstack
import utils

conn = openstack.connect(cloud_name="openstack", region_name="nz_wlg_2")

IMAGE = "ubuntu-minimal-16.04-x86_64"
FLAVOUR = "c1.c1r1"
SECURITYGROUP = "assignment2"
KEYPAIR = "qiaoy2MDB"
PUBLICNET = "public-net"

my_network_name = "qiaoy2-net"
my_cidr = "192.168.50.0/24"
my_subnet_name = "qiaoy2-subnet"
my_router_name = "qiaoy2-rtr"
server_list = ["qiaoy2-web", "qiaoy2-app", "qiaoy2-db"]

image = conn.compute.find_image(IMAGE)
flavour = conn.compute.find_flavor(FLAVOUR)
network = conn.network.find_network(my_network_name)
keypair = conn.compute.find_keypair(KEYPAIR)
security_group = conn.network.find_security_group(SECURITYGROUP)
public_net = conn.network.find_network(PUBLICNET)


def create():
    """ Create a set of Openstack resources.
    If the required resources do not exist, new one will be created.
    """
    if not conn.network.find_network(my_network_name):
        netw = utils.create_network(conn, my_network_name)
    else:
        netw = conn.network.find_network(my_network_name)
        print("Network %s exists already." % my_network_name)

    if not conn.network.find_subnet(my_subnet_name):
        subn = utils.create_subnet(conn, netw, my_subnet_name, my_cidr)
    else:
        subn = conn.network.find_subnet(my_subnet_name)
        print("Subnet %s exists already." % my_subnet_name)

    if not conn.network.find_router(my_router_name):
        rout = utils.create_router(conn, my_router_name, public_net)
        utils.add_router_interface(conn, rout, subn)
    else:
        print("Router %s exists already." % my_router_name)

    """ Check whether the provided resources exist. If they do not exist
    prompt message will show and servers creating will not continue.
    Otherwise servers will be created.
    """
    if not (image and flavour and keypair and security_group):
        print(
            "Please make sure the provided image %s, flavour %s, keypair %s or security_group %s exists already."
            % (IMAGE, FLAVOUR, KEYPAIR, SECURITYGROUP)
        )
    else:
        # Create server one by one
        for server in server_list:
            n_serv = conn.compute.find_server(server)
            if not n_serv:
                print("------------Creating server %s...--------" % server)
                print("network is %s " % conn.network.find_network(my_network_name))
                n_serv = conn.compute.create_server(
                    name=server,
                    image_id=image.id,
                    flavor_id=flavour.id,
                    networks=[{"uuid": conn.network.find_network(my_network_name).id}],
                    key_name=keypair.name,
                    security_groups=[{"sgid": security_group.id}],
                )
                conn.compute.wait_for_server(n_serv)
            else:
                print("Server %s exists already" % server)

        # Checking, creating and attaching floating ip to web server
        get_web_server = conn.get_server(name_or_id=server_list[0])
        if len(get_web_server["addresses"][my_network_name]) < 2:
            print(
                "-------- Creating and attaching floating ip to server %s"
                % server_list[0]
            )
            web_server = conn.compute.find_server(server_list[0])
            conn.create_floating_ip(network=PUBLICNET, server=web_server)


def run():
    """ Start  a set of Openstack virtual machines
    if they are not already running.
    """
    pass


def stop():
    """ Stop  a set of Openstack virtual machines
    if they are running.
    """
    pass


def destroy():
    """ Tear down the set of Openstack resources
    produced by the create action
    """
    pass


def status():
    """ Print a status report on the OpenStack
    virtual machines created by the create action.
    """
    pass


### You should not modify anything below this line ###
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "operation", help='One of "create", "run", "stop", "destroy", or "status"'
    )
    args = parser.parse_args()
    operation = args.operation

    operations = {
        "create": create,
        "run": run,
        "stop": stop,
        "destroy": destroy,
        "status": status,
    }

    action = operations.get(
        operation, lambda: print("{}: no such operation".format(operation))
    )
    action()
