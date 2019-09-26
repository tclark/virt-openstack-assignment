import argparse
import openstack
import time

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






