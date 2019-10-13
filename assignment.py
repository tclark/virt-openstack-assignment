import argparse
import openstack


#create connection to openstack
conn = openstack.connect(cloudname='openstack')
def create():
    
    #collect variables
    n_flavour = conn.compute.find_flavor('c1.c1r1')
    n_image = conn.compute.find_image('ubuntu-minimal-16.04-x86_64')
    n_keypair = conn.compute.find_keypair('assign')
    n_network = conn.network.find_network('shinrl1-net')
    n_public_net = conn.network.find_network('public-net')
    n_subnet = conn.network.find_subnet('shinrl1-subnet')
    CIDR = "192.168.50.0/24"
    n_webserver = conn.compute.find_server('shinrl1-web')
    n_security_group = conn.network.find_security_group('assignment2')
    n_router = conn.network.find_router('shinrl1-rtr')

    #c eate network
    if not n_network:
        network = conn.network.create_network(name='shinrl1-net')
        print(network)
        subnet='shinrl1-subnet',
        network_id=network.id,
        ip_version='4',
        cidr='192.168.50.0/24'
        gateway_ip='192.168.50.1'
        print("Network created ^_^")
    else:
        print("Network Borked")
    
    #create subnet
    if not n_subnet: 
        subnet = conn.network.create_subnet(name='shinrl1-subnet',
                network_id=network.id, ip_version='4', cidr=CIDR)
        print("Subnet Created")
    else:
        print("Subnet borked") 
    #create router
    
    if not n_router:
    
        args = {'name': "shinrl1-rtr", 'external_gateway_info': {'network_id': n_public_net.id}}
        router = conn.network.create_router(**args)
        conn.network.add_interface_to_router(n_router, subnet.id)

        print("Router Created ^_^")
    else:
        print ("Router Borked")

    #reaete servers
    if not n_webserver:
        #conn.network.add_interface_to_router(n_router, subnet_id=n_network.subnet_ids[0])
        webserver = conn.compute.create_server(name="shinrl1-web", image_id=n_image.id,  flavor_id=n_flavour.id, networks=[{"uuid": network.id}], key_name=n_keypair.name)
        webserver = conn.compute.wait_for_server(webserver)
        conn.compute.add_security_group_to_server(webserver, n_security_group)
        print("shinrl1-web up")
    #add floating ips to servers
        webserver_ip = conn.network.create_ip(floating_network_id=n_public_net.id)
        conn.compute.add_floating_ip_to_server(webserver, address=webserver_ip.floating_ip_address)
        print ("ip attatched to web server:", webserver_ip.floating_ip_address)

        print("floating ip attatched to shinrl1-web")
    else:
        print("Server bORKED")
    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    
    n_router = conn.network.find_router('shinrl1-rtr')
    n_network = conn.network.find_network('shinrl1-net')
    n_subnet = conn.network.find_subnet('shinrl1-subnet')
    n_webserver = conn.compute.find_server('shinrl1-web')
    if n_router:
        conn.network.delete_router(n_router, ignore_missing=True)
        print("rtr deleted")
    else:
        print("rtr deletion error")
    if n_network:
        conn.network.delete_network('shinrl1-net')
        print("network deleted")
    else:
        print("network deletion error")
    if n_subnet:
        conn.network.delete_subnet('shinrl1-subnet')
        print("subnet deleted")
    else:
        print("subnet deletion error")
    if n_webserver:
        conn.compute.delete_server('shinrl1-web')
        print("webserver deleted")
    else:
        print("webserver deletion error")
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    def list_networks(conn):
        print("List Networks:")

    for network in conn.network.networks():
        print(network)

    pass


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
