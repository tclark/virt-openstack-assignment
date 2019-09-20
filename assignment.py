import argparse
import openstack


global conn 
conn = openstack.connect(cloud_name='openstack')

serverList = ["dackja1-app", "dackja1-db", "dackja1-web"]

def create():
    ''' Create a set of Openstack resources '''
    conn = openstack.connect(cloud_name='openstack')

    network=conn.network.create_network(
        name='dackja1-net'
    )

    subnet = conn.network.create_subnet(
        name = 'dackja1-subnet',
        network_id=network.id,
        ip_version='4',
        cidr='192.168.50.0/24',
        gateway_ip='192.168.50.1'
    )

    public_net = conn.network.find_network('public-net')
   
    router = conn.network.create_router(
        name='dackja1-rtr',
        external_gateway_info={'network_id': public_net.id}
        
    )

    pass

    IMAGE = 'ubuntu-minimal-16.04-x86_64'
    FLAVOUR = 'c1.c1r1'
    Network = 'private-net'
    KEYPAIR = 'dackja1-key'

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    network = conn.network.find_network(Network)
    keypair = conn.compute.find_keypair(KEYPAIR)

    for serverName in serverList:
        
        SERVER = serverName
        server =conn.compute.create_server(
        name=SERVER, image_id=image.id, flavor_id=flavour.id,
        networks=[{"uuid": network.id}], key_name=keypair.name)
        server = conn.compute.wait_for_server(server)
        

        if serverName == "dackja1-web":
            floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
            web = conn.compute.find_server("dackja1-web")
            conn.compute.add_floating_ip_to_server(web, floating_ip.floating_ip_address)

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''

    for name in serverList:
        server = conn.compute.find_server(name_or_id=name)
        if server is not None:
            ser = conn.compute.get_server(server)
            if ser.status == "SHUTOFF":
                conn.compute.start_server(server)
            elif ser.status == "ACTIVE":
                print("yote")

            else:
                print(name + "ye")

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

    conn = openstack.connect(cloud_name='openstack')
 
    network = conn.network.find_network("dackja1-net")
    delNetwork = conn.network.delete_network(network)
    print("Network Destroyed")
    router = conn.network.find_router("dackja1-rtr")
    delRouter = conn.network.delete_router(router)
    print("Router Destroyed")

    for server in serverList:
        ser = conn.compute.find_server(name_or_id=server)
        if ser is not None:
            conn.compute.delete_server(ser)
            print(ser.name + " Destroyed.")
        else:
            print(server + " does not exist.")

    pass

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
