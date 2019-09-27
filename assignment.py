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
    prompt message will show. Otherwise servers will be created.
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
                print("network is %s " % conn.network.find_network("qiaoy2-net"))
                n_serv = conn.compute.create_server(
                    name=server,
                    image_id=image.id,
                    flavor_id=flavour.id,
                    networks=[{"uuid": conn.network.find_network("qiaoy2-net").id}],
                    key_name=keypair.name,
                    security_groups=[{"sgid": security_group.id}],
                )
                conn.compute.wait_for_server(n_serv)
            else:
                print("Server %s exists already" % server)

        """
        Find, check and add floating ip to web server if no floating ip for it
        if server == "qiaoy2-web":
            conn.compute.wait_for_server(n_serv)
            print("-------Adding floating ip to the web server...------")
            floating_ip = conn.network.create_ip(
                floating_network_id=public_net.id
            )
            conn.compute.add_floating_ip_to_server(
                n_serv, floating_ip.floating_ip_address
            )
            print(
                "Web server floating ip address is: %s"
                % floating_ip.floating_ip_address
            )"""


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
