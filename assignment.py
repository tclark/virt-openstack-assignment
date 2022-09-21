import argparse
from http import server
import openstack

## command to source python enviroment to run script
# source id720/bin/activate
# source tom-clark-openrc.sh


IMAGE = 'ubuntu-minimal-22.04-x86_64'
FLAVOUR = 'c1.c1r1'
NETWORK = 'wintst1-net'
SUBNET = 'wintst1-subnet'
KEYPAIR = 'wintst1-key'
SERVERNAMES = ['wintst1-app', 'wintst1-db', 'wintst1-web']
ROUTER = 'wintst1-rtr'
IPV = '4'
CIDR = '192.168.50.0/24'


conn = openstack.connect(cloud_name='catalystcloud')

#Generate new SSH key if one does not alreay exist
def keygen():
   
    if not conn.compute.find_keypair(KEYPAIR):
        print('creating new keypair')
        keypair = conn.compute.create_keypair(name=KEYPAIR)

    else:
        keypair = conn.compute.find_keypair(KEYPAIR)
        print('keypair exists')

    return keypair

#Create function to deploy servers, network and router.
def create():

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    security_group = conn.network.find_security_group('assignment2')
    public_net = conn.network.find_network('public-net')
    keypair = keygen()

    #Creating the virtual network
    if not conn.network.find_network(NETWORK): 
        network = conn.network.create_network(name=NETWORK)
        print('Netowrk ' + NETWORK + ' Created')

    else:
        network = conn.network.find_network(NETWORK)
        print('Network ' + NETWORK + ' Exists') 

    #Creating the virtual subnet
    if not conn.network.find_subnet(SUBNET):
        subnet = conn.network.create_subnet(
            name=SUBNET, network_id=network.id, 
            ip_version=IPV, cidr=CIDR
            )
            
        print('Subnet ' + SUBNET + ' Created')

    else:
        subnet = conn.network.find_subnet(SUBNET)
        print('Subnet ' + SUBNET + ' Exists')

    #Creating the router
    if not conn.network.find_router(ROUTER):
        router = conn.network.create_router(
            name=ROUTER, 
            external_gateway_info={'network_id': public_net.id}
            )

        conn.network.add_interface_to_router(router, subnet.id)
        print('Router ' + ROUTER + ' Created')
    else:
        router = conn.network.find_router(ROUTER)
        print('Router ' + ROUTER + ' Exists')

   
   #Creating three Servers
    print('Creating Servers...')

    for name in SERVERNAMES: 
        server_name = name

        if not conn.compute.find_server(name):
            server = conn.compute.create_server(
                name=server_name, 
                image_id=image.id, 
                flavor_id=flavour.id, 
                networks=[{"uuid": network.id}], 
                key_name=keypair.name, 
                security_groups=[{'name':security_group.id}]
                )

            server = conn.compute.wait_for_server(server)
            print('Server: ' + name + ' Created')

            # Creating and assigning a floating Ip to the web server
            if server.name == 'wintst1-web':
                floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
                server = conn.compute.find_server('wintst1-web')
                conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)

        else:
            print('Server: ' + name + ' Exists')
pass

#Start the servers if they are not already running 
def run():

    for name in SERVERNAMES:
        
        if conn.compute.find_server(name) is not None:
            server = conn.compute.find_server(name)
            state = conn.compute.get_server(server)
        
            if state.status == 'SHUTOFF':
                conn.compute.start_server(server)
                print(server.name + ' Has been started.')

            else:
                print(server.name + ' is already running.')
        else:
            print('Could not start ' + name + '. Server does not exist')
pass

#Stop the servers if they are running
def stop():

 for name in SERVERNAMES:
        
        if conn.compute.find_server(name) is not None:
            server = conn.compute.find_server(name)
            state = conn.compute.get_server(server)
        
            if state.status == 'ACTIVE':
                conn.compute.stop_server(server)
                print(server.name + ' Has been stopped.')

            else:
                print(server.name + ' is already off.')
        else:
            print('Could not shutdown ' + name + '. Server does not exist')
pass


#Delete the set of openstack resources created in this scrpit 
def destroy():

    router = conn.network.find_router(ROUTER)
    subnet = conn.network.find_subnet(SUBNET)
    network = conn.network.find_network(NETWORK)

    #find all the servers 
    for name in SERVERNAMES: 

        if conn.compute.find_server(name_or_id=name) is not None:
            server = conn.compute.find_server(name)

            # removes the floating IP address from the web server 
            if server.name == 'wintst1-web':
                conn.network.delete_ip(
                    conn.network.find_ip(
                      conn.compute.get_server(server).addresses['wintst1-net'][1]['addr']
                   )
                )

                print('floating Ip deleted from ' + server.name)

            conn.compute.delete_server(server)
            print(name + ' Deleted')

        else:
            print('Could not delete ' + name + ' because it does not exist.')

     # Delete the router
    if conn.network.find_router(ROUTER) is not None:
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(router)
        print('Router ' + router.name + ' has been deleted.')
    else:
        print('Could not delete router becuase it does not exist.')

    #Delete the subnet
    if conn.network.find_subnet(SUBNET) is not None:
        conn.network.delete_subnet(subnet, ignore_missing=False)
        print('Subnet ' + subnet.name + ' has been deleted.')
    else: 
        print('Could not delete subnet becasue it does not exist.')

    #Delete the network
    if conn.network.find_network(NETWORK) is not None:
        conn.network.delete_network(network, ignore_missing=False)
        print('Network ' + network.name + ' has been deleted.')
    else:
        print('Could not delete network becasue it does not exist.')

pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
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
