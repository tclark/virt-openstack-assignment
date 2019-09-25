import argparse
import openstack

conn = openstack.connect(cloud_name='openstack',region_name='nz_wlg_2')

#from neutronclient.v2_0 import client
#from credentials import get_credentials

my_network_name = 'qiaoy2-net'
my_cidr = '192.168.50.0/24'
my_subnet_name = 'qiaoy2-subnet'
my_router_name = 'qiaoy2-rtr'
public_net_name='public-net'
def create_network(conn, network_name):
    try:
        print("--------------Creating network...---------------")
        n_netw = conn.create_network(name=network_name, admin_state_up=True)
        print('Network %s created' % n_netw)
        print(type(n_netw))
        return n_netw
    finally:
        print("*************Network creating completed****************")

def create_subnet(conn, network_name, subnet_name, cidr_r):
    try:
        print("---------------Creating subnet...--------------")
        n_subn = conn.create_subnet(name=subnet_name, network_name_or_id=network_name.id, cidr=cidr_r)
        print('Created subnet %s' % n_subn)
        return n_subn
    finally:
        print("*****************Subnet creating completed**************")

def create_router(conn, router_name,external_network):
    try:
        print("--------------Creating router...-------------------- ")
        print("the external network is %s" % external_network)
        n_rout = conn.network.create_router(name=router_name,external_gateway_info={'network_id': external_network.id})
        print('Created rounter %s' % n_rout)
        return n_rout
    finally:
        print("****************Router creating completed***************")

def add_router_interface(conn, router_name, subnet_name):
    try:
        print("--------------Add router interface...----------------- ")
        #print("subnet type is %s " % type(subnet_name))
        conn.add_router_interface(router_name, subnet_id = subnet_name.id)
    finally:
        print("Router interface is added completely")
        

if not (conn.network.find_network(my_network_name)):
    netw = create_network(conn, my_network_name)
else:
    print('Network %s exists already.' % my_network_name)


if not (conn.network.find_subnet(my_subnet_name)):
    subn = create_subnet(conn, netw, my_subnet_name, my_cidr)
else:
    subn = conn.network.find_subnet(my_subnet_name)
    print('subnet is %s ' % subn)
    print('Subnet %s exists already.' %my_subnet_name)

public_net = conn.network.find_network(public_net_name)
rout = create_router(conn, my_router_name, public_net)

add_router_interface(conn, rout, subn)
#conn.add_router_interface(rout, external_gateway_info={'network_id': public_net.id})
