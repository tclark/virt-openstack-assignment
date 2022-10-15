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
IMAGE = "ubuntu-minimal-22.04-x86_64"
FLAVOUR = "c1.c1r1"
WEB_NAME = "westcl4-web"
APP_NAME = "westcl4-app"
DB_NAME = "westcl4-db"

# run constants

# stop constants