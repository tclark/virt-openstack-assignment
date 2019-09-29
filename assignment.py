"""
API reference
https://docs.openstack.org/openstacksdk/latest/user/connection.html
https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
"""
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
router = conn.network.find_router(my_router_name)
subnet = conn.network.find_subnet(my_subnet_name)
get_web_server = conn.get_server(name_or_id=server_list[0])
find_web_server = conn.compute.find_server(server_list[0])

def create():
    """ Create a set of Openstack resources.
    If the required resources do not exist, new one will be created.
    """
    if not network:
        netw = utils.create_network(conn, my_network_name)
    else:
        netw = network
        print("Network %s exists already." % my_network_name)

    if not subnet:
        subn = utils.create_subnet(conn, netw, my_subnet_name, my_cidr)
    else:
        subn = subnet
        print("Subnet %s exists already." % my_subnet_name)

    if not router:
        rout = utils.create_router(conn, my_router_name, public_net)
        utils.add_router_interface(conn, rout, subn)
    else:
        rout = router
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
                print("------------ Creating server %s... --------" % server)
                n_serv = conn.compute.create_server(
                    name=server,
                    image_id=image.id,
                    flavor_id=flavour.id,
                    networks=[{"uuid": conn.network.find_network(my_network_name).id}],
                    key_name=keypair.name,
                    security_groups=[{"sgid": security_group.id}],
                )
                conn.compute.wait_for_server(n_serv,wait=180)
            else:
                print("Server %s exists already" % server)

        # Checking, creating and attaching floating ip to web server
        get_web_server = conn.get_server(name_or_id=server_list[0])
        if not get_web_server["interface_ip"]:
            print(
                "-------- Creating and attaching floating ip to server %s --------"
                % server_list[0]
            )
            conn.compute.wait_for_server(n_serv)
            conn.create_floating_ip(network=PUBLICNET, server=find_web_server)
        else:
            print("Floating ip is attached to server %s already" % server_list[0])


def run():
    """ Start  a set of Openstack virtual machines
    if they are not already running.
    """
    for server in server_list:
        get_server = conn.get_server(name_or_id=server)
        if get_server:
            if get_server.status not in ["Active"]:
                print("------- Starting server %s... --------" % server)
                conn.compute.start_server(server)
                conn.compute.wait_for_server(conn.compute.find_server(server))
            else:
                print("Server %s is running already" % server)
        else:
            print(
                "Server %s can not be got. Please check wthether the server exists."
                % server
            )


def stop():
    """ Stop  a set of Openstack virtual machines
    if they are running.
    """


def destroy():
    """ Tear down the set of Openstack resources
    produced by the create action
    """

    # Detach and releasing floating ip for the web server
    list_ips = conn.list_floating_ips()
    if get_web_server and list_ips:
        web_server_ip = get_web_server["interface_ip"]
        ip_id = None
        for ipa in list_ips:
            if ipa["floating_ip_address"] == web_server_ip:
                ip_id = ipa["id"]
                break
        if ip_id:
            print(
                "Detaching floating ip with id %s from server %s"
                % (ip_id, server_list[0])
            )
            conn.detach_ip_from_server(find_web_server.id, ip_id)
            conn.delete_floating_ip(ip_id, retry=3)
    # Delete servers one by one
    for server in server_list:
        find_server = conn.compute.find_server(server)
        if find_server:
            print("------ Deleteing server %s... ---------" % server)
            conn.compute.delete_server(find_server)
    # Delete router
    if router:
        print("------ Removing interface from router %s... -------" % my_router_name)
        conn.network.remove_interface_from_router(router, subnet.id)
        print("------ Deleteing router %s...--------" % my_router_name)
        conn.network.delete_router(router)
    # Delete network
    if network:
        print("------ Deleteing network %s... ---------" % my_network_name)
        conn.network.delete_network(network)
    # Delete Subnet
    if subnet:
        print("------ Deleteing subnet %s... ---------" % my_subnet_name)
        conn.network.delete_subnet(subnet)


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
