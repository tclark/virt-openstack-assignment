# file containing constants for the assignment project.
import openstack

# network constants
CONN = openstack.connect(cloud_name='openstack', region_name='nz-por-1')

USER = "westcl4"
NETWORK = "westcl4_net"
SUBNET = "westcl4_subnet"
VPC = "westcl4_vpc"
NETWORK = "westcl4_net"
CIDR = "192.168.50.0/24"
GATEWAY_IP = "192.168.50.1"
ROUTERNAME = "westcl4-rtr"



# compute constants

# run constants

# stop constants