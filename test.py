import argparse
import openstack
import time

conn = openstack.connect(cloud_name="openstack", region_name="nz_wlg_2")

IMAGE = "ubuntu-minimal-16.04-x86_64"
FLAVOUR = "c1.c1r1"
SECURITYGROUP = "assignment2"
KEYPAIR = "qiaoy2MDB"

my_network_name = "qiaoy2-net"
my_cidr = "192.168.50.0/24"
my_subnet_name = "qiaoy2-subnet"
my_router_name = "qiaoy2-rtr"
public_net_name = "public-net"
server_list = ["qiaoy2-web", "qiaoy2-app", "qiaoy2-db"]

image = conn.compute.find_image(IMAGE)
flavour = conn.compute.find_flavor(FLAVOUR)
network = conn.network.find_network(my_network_name)
keypair = conn.compute.find_keypair(KEYPAIR)
security_group = conn.network.find_security_group(SECURITYGROUP)
#public_net = conn.network.find_network(public_net_name)


def create_network(conn_obj, network_name):
    try:
        print("--------------Creating network...---------------")
        n_netw = conn_obj.create_network(name=network_name, admin_state_up=True)
        print("Network %s created" % n_netw)
        print(type(n_netw))
        return n_netw
    finally:
        print("*************Network creating completed****************")


def create_subnet(conn_obj, network_obj, subnet_name, cidr_r):
    try:
        print("---------------Creating subnet...--------------")
        n_subn = conn_obj.create_subnet(
            name=subnet_name, network_name_or_id=network_obj.id, cidr=cidr_r
        )
        print("Created subnet %s" % n_subn)
        return n_subn
    finally:
        print("*****************Subnet creating completed**************")


def create_router(conn_obj, router_name, ext_network_obj):
    try:
        print("--------------Creating router...-------------------- ")
        print("the external network is %s" % ext_network_obj)
        n_rout = conn_obj.network.create_router(
            name=router_name, ext_gateway_info={"network_id": ext_network_obj.id}
        )
        print("Created rounter %s" % n_rout)
        return n_rout
    finally:
        print("****************Router creating completed***************")


def add_router_interface(conn_obj, router_obj, subnet_obj):
    try:
        print("--------------Add router interface...----------------- ")
        conn_obj.add_router_interface(router_obj, subnet_id=subnet_obj.id)
    finally:
        print("Router interface is added completely")


if not conn.network.find_network(my_network_name):
    netw = create_network(conn, my_network_name)
else:
    netw = conn.network.find_network(my_network_name)
    print("Network %s exists already." % my_network_name)


if not conn.network.find_subnet(my_subnet_name):
    subn = create_subnet(conn, netw, my_subnet_name, my_cidr)
else:
    subn = conn.network.find_subnet(my_subnet_name)
    print("Subnet %s exists already." % my_subnet_name)


if not conn.network.find_router(my_router_name):
    public_net = conn.network.find_network(public_net_name)
    rout = create_router(conn, my_router_name, public_net)
    add_router_interface(conn, rout, subn)
else:
    print("Router %s exists already." % my_router_name)


for server in server_list:
    n_serv = conn.compute.find_server(server)
    if not n_serv:
        print("------------Creating server %s...--------" % server)
        print("network is %s " % conn.network.find_network('qiaoy2-net'))
        n_serv = conn.compute.create_server(
            name=server,
            image_id=image.id,
            flavor_id=flavour.id,
            networks=[{"uuid": conn.network.find_network('qiaoy2-net').id}],
            key_name=keypair.name,
            security_groups=[{"sgid": security_group.id}],
        )

        if server == "qiaoy2-web":
            conn.compute.wait_for_server(n_serv)
            print("-------Adding floating ip to the web server...------")
            floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
            conn.compute.add_floating_ip_to_server(
                server, floating_ip.floating_ip_address
            )
            print(
                "Web server floating ip address is: %s"
                % floating_ip.floating_ip_address
            )
    else:
        print("Server %s exists already" % server)

