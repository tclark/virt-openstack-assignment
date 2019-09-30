"""
Author: Yandong Qiao
Date: September, 2019
Email: yandongqiao@gmail.com
https://docs.openstack.org/openstacksdk/latest/user/connection.html
https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
"""


def create_network(conn_obj, network_name):
    try:
        print("------------ Creating network... --------------")
        n_netw = conn_obj.create_network(name=network_name, admin_state_up=True)
        print("Created network {} ".format(n_netw))
        return n_netw
    finally:
        print("Network is created successfully")


def create_subnet(conn_obj, network_obj, subnet_name, cidr_r):
    try:
        print("------------ Creating subnet... ------------")
        n_subn = conn_obj.create_subnet(
            name=subnet_name, network_name_or_id=network_obj.id, cidr=cidr_r
        )
        print("Created subnet {}".format(n_subn))
        return n_subn
    finally:
        print("Subnet is created successfully")


def create_router(conn_obj, router_name, ext_network_obj):
    try:
        print("------------- Creating router... -------------------- ")
        n_rout = conn_obj.network.create_router(
            name=router_name, external_gateway_info={"network_id": ext_network_obj.id}
        )
        print("Created rounter {}".format(n_rout))
        return n_rout
    finally:
        print("Router is created successfully")


def add_router_interface(conn_obj, router_obj, subnet_obj):
    try:
        print("---------- Adding router interface...----------------- ")
        conn_obj.add_router_interface(router_obj, subnet_id=subnet_obj.id)
    finally:
        print("Router interface is added successfully")
