import argparse
import openstack

# connect to OpenStack
conn = openstack.connect(cloud_name='openstack', region_name='nz-hlz-1a')

# Variables
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOR = 'c1.c1r1'
SECURITYGROUP = "assignment2"
KEYPAIR = 'chauw2key'
PUBLICNET = 'public-net'
CIDR = '192.168.50.0/24'
NETWORK = 'chauw2-net'
SUBNET = 'chauw2-subnet'
ROUTER = 'chauw2-rtr'
ALLSERVERSLIST = ['chauw2-web', 'chauw2-app', 'chauw2-db']
WEB_SERVER = 'chauw2-web'
APP_SERVER = 'chauw2-app'
DB_SERVER = 'chauw2-db'

# Create openstack rescore
# https://docs.openstack.org/openstacksdk/latest/user/guides/compute.html
image = conn.compute.find_image(IMAGE)
flavor = conn.compute.find_flavor(FLAVOR)
keypair = conn.compute.find_keypair(KEYPAIR)
security_group = conn.network.find_security_group(SECURITYGROUP)
network = conn.network.find_network(NETWORK)
router = conn.network.find_router(ROUTER)
subnet = conn.netowork.find_subnet(SUBNET)
publicnet = conn.network.find_network(PUBLICNET)

def create():
    ''' Create a set of Openstack resources '''
     #Find network
    print("Searching Network...")
    network = conn.network.find_network(NETWORK)
    if network is None:
      print('Creating', NETWORK)
      network = conn.network.create_network(name=NETWORK)
    else:
      print(NETWORK, 'exists in the network')

    # Find Subnet
    subnet = conn.network.find_subnet(SUBNET)
    print("Searching Subnet...")
    if subnet is None:
        print('Creating', SUBNET)
        subnet = conn.network.create_subnet(name=SUBNET,network_id=network.id,cidr=CIDR,ip_verison=4)
    else:
        print(SUBNET, 'exists in the network')
    
    # Find Router
    # https://docs.catalystcloud.nz/first-instance/shade-sdk.html
    router = conn.network.find_router(ROUTER)
    if router is None:
      print('Creating' , ROUTER)
      router = conn.network.create_router(name=ROUTER, external_gateway_info={"network_id": publicnet.id})
      conn.network.add_interface_to_router(router, subnet.id)
    else:
      print(ROUTER, 'exists in the network')

    # Create floation IP
    print("Creating Floating IP")
    floatingip = conn.network.create_ip(floating_network_id=publicnet.id)

    #Find Server (WEB)
    print("Searching WEB Server...")
    web_server = conn.compute.find_server(WEB_SERVER)
    if web_server is None:
        print("Creating Web Server...")
        web_server = conn.compute.create_server(
            name=WEB_SERVER, 
              image_id=image.id, 
              flavor_id=flavor.id, 
              networks=[{"uuid": conn.compute.network.find_network(NETWORK).id}], 
              key_name=keypair.name ,
              security_groups=[{"sgid":security_group.id}]
        )
    else:
        print(WEB_SERVER,"WEB server already exist in the network")
        print("------------------------------")
    
      #Find Server (DB)
    print("Searching DB Server...")
    web_server = conn.compute.find_server(DB_SERVER)
    if web_server is None:
        print("Creating DB Server...")
        db_server = conn.compute.create_server(
            name=DB_SERVER, 
              image_id=image.id, 
              flavor_id=flavor.id, 
              networks=[{"uuid": conn.compute.network.find_network(NETWORK).id}], 
              key_name=keypair.name ,
              security_groups=[{"sgid":security_group.id}]
        )
        print("Waiting for the server to come up")
        db_server = conn.compute.wait_for_server(db_server)
    else:
        print(DB_SERVER,"DB server already exist in the network")
        print("------------------------------")

      #Find Server (APP)
    print("Searching APP Server...")
    app_server = conn.compute.find_server(APP_SERVER)
    if app_server is None:
        print("Creating APP Server...")
        app_server = conn.compute.create_server(
            name=APP_SERVER, 
              image_id=image.id, 
              flavor_id=flavor.id, 
              networks=[{"uuid": conn.compute.network.find_network(NETWORK).id}], 
              key_name=keypair.name ,
              security_groups=[{"sgid":security_group.id}]
        )        
    else:
        print(APP_SERVER,"APP server already exist in the network")
        print("------------------------------")
    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
     '''
    web_server = conn.compute.find_server(WEB_SERVER)
    if web_server is None:
        print("Cannot find server")
    else:
        web_server = conn.compute.get_server(WEB_SERVER)
        web_server = conn.compute.start_server(WEB_SERVER)
        print("Waiting for WEB server to come up")
        web_server = conn.compute.wait_for_server(web_server)
    app_server = conn.compute.find_server(APP_SERVER)
    db_server = conn.compute.find_server(DB_SERVER)
    '''
    for servername in ALLSERVERSLIST:
        server = conn.compute.find_server(servername)
        if server is None:
             print("Cannot find server")
        else:
            server = conn.compute.get_server(server)
        if server.status != 'ACTIVE':
            conn.compute.start_server(server)
            server = conn.compute.wait_for_server(server)
    
    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    #app_server = conn.compute.find_server(APP_SERVER)
    #db_server = conn.compute.find_server(DB_SERVER)

    
    for servername in ALLSERVERSLIST:
        server = conn.find_server(servername) #find each server from the list
        if server.status == 'ACTIVE':
            print("The server is currently active")
            print("Stopping server now")
            conn.compute.stop_server(server)
        else:
            print("server already stop")
    pass

def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    print("Deleting  Network...")
    network = conn.network.find_network(NETWORK)
    router = conn.network.find_router(ROUTER)
    subnet = conn.netowork.find_subnet(SUBNET)

    '''
    for example_subnet in example_network.subnet_ids:
        conn.network.delete_subnet(example_subnet, ignore_missing=False)
    conn.network.delete_network(example_network, ignore_missing=False) 
   '''
   #delete server for loop
   '''
    for servername in ALLSERVERSLIST:
        server = conn.find_server(servername) #find each server from the list
        if server.status == 'ACTIVE':
            conn.compute.get_server(server)
            conn.compute.delete_server(server)
        else:
            print("server already deleted")
   #conn.network.delete_network(NETWORK, ignore_missing=False)
   '''
   #delete WEB server
    if WEB_SERVER is None:
        print("Web Sever already deleted")
    else:
        print("Deleting Web Server...")
        conn.compute.get_server(WEB_SERVER) #get server
        #con.compute.stop_server(WEB_SERVER) #stop server if didnt stop
        webip = conn.compute.server_ips(WEB_SERVER.id) #find web ip address
        conn.network.remove_floating_ip_from_server(WEB_SERVER,webip)
        conn.compute.delete_server(WEB_SERVER) #delete server
       
    #delete APP server
    if APP_SERVER is None:
        print('App Server already deleted')
    else:
        print("Deleting App Server...")
        conn.compute.get_server(APP_SERVER) #get server
        #con.compute.stop_server(APP_SERVER) #stop server if didnt stop
        conn.compute.delete_server(APP_SERVER) #delete server
        print('Delete App server')

    #delete DB server
    if DB_SERVER is None
        print('DB Server already deleted')
    else:
        print("Deleting DB Server...")
        conn.compute.get_server(DB_SERVER) #get server
        #con.compute.stop_server(DB_SERVER) #stop server if didnt stop
        conn.compute.delete_server(DB_SERVER) #delete server
        print('Delete DB server')

    #delete router
    print("deleting router")
    if router is None:
        print("Router doesn't exist in the netowork")
    else:
        conn.network.delete_router(router)
        print("Router has been deleted")

    #delete subnet
    print("deleting subnet")
    if subnet is None:
        print("Subnet doesn't exist in the network")
    else:
        conn.network.delete_subnet(subnet)
        print("Subnet has been deleted")

    #delete network 
    print("deleting network")
    if network is None:
        print("network doesn't exist in the network")
    else:
        conn.netowork.delete_network(network)
        print("Network has been deleted")
    
    print("Delete process completed")

    '''       
     for servername in ALLSERVERSLIST:
    server = conn.compute.find_server(server)
    if server is None:
    print("Server deleted/does not exist")
    '''
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    web_server = conn.compute.find_server(WEB_SERVER)
    app_server = conn.compute.find_server(APP_SERVER)
    db_server = conn.compute.find_server(DB_SERVER)
    
    print("----Server Status----")
        if web_server is None:
            print("Web server doesn't exist")
        else:
            print("Web server status")
            web_server = conn.compute.get_server(web_server.id)
            print(web_server.name)
            web_status = web_server.status
            print("Status:", str(web_status))
            web_ip = conn.compute.server_ips(web_server.id)
            print("Web server IP address:")
            for address in web_ip:
            print(str(address.network_label), str(address.address))
			
		if app_server is None:
			 print("APP server doesn't exist")
		else:
			print("APP server status")
            app_server = conn.compute.get_server(app_server.id)
            print(app_server.name)
            app_status = app_server.status
            print("Status:", str(app_status))
            app_ip = conn.compute.server_ips(app_server.id)
            print("APP server IP address:")
            for address in app_ip:
            print(str(address.network_label), str(address.address))
		
		if db_server is None:
			print("DB server doesn't exist")
		else:
			print("DB server status")
            db_server = conn.compute.get_server(db_server.id)
            print(db_server.name)
            db_status = db_server.status
            print("Status:", str(db_status))
            db_ip = conn.compute.server_ips(db_server.id)
            print("DB server IP address:")
            for address in db_ip:
            print(str(address.network_label), str(address.address))
		print("End of the status report")
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
