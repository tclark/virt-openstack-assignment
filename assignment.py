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
    n_appserver = conn.compute.find_server('shinrl1-app')
    n_dbserver = conn.compute.find_server('shinrl1-db')
    
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
    
    #reate subnet
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
        
        #conn.network.add_interface_to_router(n_router, subnet_id=n_subnet.id)
       # conn.network.add_interface_to_router(n_router, subnet_id=n_network.subnet_ids[0])
        webserver = conn.compute.create_server(name="shinrl1-web", image_id=n_image.id,  flavor_id=n_flavour.id, networks=[{"uuid": network.id}], key_name=n_keypair.name)
        webserver = conn.compute.wait_for_server(webserver)
        conn.compute.add_security_group_to_server(webserver, n_security_group)
        print("shinrl1-web up")
        #floating_ip = conn.network.create_ip(floating_network_id=n_public_net.id)
        #conn.compute.add_floating_ip_to_server(webserver, floating_ip.floating_ip_address)
        
    else:
        print("web server borked")
    if not n_appserver:
        appserver = conn.compute.create_server(name="shinrl1-app", image_id=n_image.id,  flavor_id=n_flavour.id, networks=[{"uuid": network.id}], key_name=n_keypair.name)
        appserver = conn.compute.wait_for_server(appserver)
        conn.compute.add_security_group_to_server(appserver, n_security_group)
        print("shinrl1-app up")
    else:
        print("app server borked")


    if not n_dbserver:
        dbserver = conn.compute.create_server(name="shinrl1-db", image_id=n_image.id,  flavor_id=n_flavour.id, networks=[{"uuid": network.id}], key_name=n_keypair.name)
        dbserver = conn.compute.wait_for_server(dbserver)
        conn.compute.add_security_group_to_server(dbserver, n_security_group)
        print("shinrl1-db up")
    else:
        print("db server borked")

    
    add_floating_ip_to_server(n_webserver, n_public_net)
        

    if not n_appserver:
        appserver = conn.compute.create_server(name="shinrl1-app", image_id=n_image.id,  flavor_id=n_flavour.id, networks=[{"uuid": network.id}], key_name=n_keypair.name)
        appserver = conn.compute.wait_for_server(appserver)
        conn.compute.add_security_group_to_server(appserver, n_security_group)
        print("shinrl1-app up")
    else:
        print("db server borked")
        
    
    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    n_webserver = conn.compute.find_server('shinrl1-web')
    n_appserver = conn.compute.find_server('shinrl1-app')
    n_dbserver = conn.compute.find_server('shinrl1-db')

    if not n_webserver:
        print("shinrl1-web not found, cannot start")
    else:
        conn.compute.start_server(n_webserver.id)
        print("webserver started"
                )
    if not n_appserver:
        print("shinrl1-app not found, cannot start")
    else:
        conn.compute.start_server(n_appserver.id)
        print("appserver started")
    if not n_dbserver:
        print("shinrl1-db not found, cannot start")
    else:
        conn.compute.start_server(n_dbserver.id)
        print("dbserver started")

    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    n_webserver = conn.compute.find_server('shinrl1-web')
    n_appserver = conn.compute.find_server('shinrl1-app')
    n_dbserver = conn.compute.find_server('shinrl1-db')
    
    if not n_webserver:
        print("webserver not found, cannot stop")
    else:
        conn.compute.stop_server(n_webserver.id)
        print("webserver stopped")

    if not n_appserver:
        print("appserver not found, cannot stop")
    else:
        conn.compute.stop_server(n_appserver.id)
        print("appserver stopped")

    if not n_dbserver:
        print("cbserver not found, cannot stop")
    else:
        conn.compute.stop_server(n_dbserver.id)
        print("dbserver stopped")
                                              

    pass
def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    
    n_router = conn.network.find_router('shinrl1-rtr')
    n_network = conn.network.find_network('shinrl1-net')
    n_subnet = conn.network.find_subnet('shinrl1-subnet')
    n_webserver = conn.compute.find_server('shinrl1-web')
    n_appserver = conn.compute.find_server('shinrl1-app')
    n_dbserver = conn.compute.find_server('shinrl1-db')

    if n_webserver:
        conn.compute.delete_server(n_webserver)
        print("webserver deleted")
    else:
        print("webserver deletion error")
    if n_appserver:
        conn.compute.delete_server(n_appserver)
        print("appserver deleted")
    else:
        print("appserver deletion error")
    if n_dbserver:
        conn.compute.delete_server(n_dbserver)
        print("dbserver deleted")
    else:
        print("dbserver deletion error")
    if n_router:
        conn.network.delete_router(n_router)
        print("rtr deleted")
    else:
        print("rtr deletion error")
    if n_subnet:
        conn.network.delete_subnet(n_subnet)
        print("subnet deleted")
    else:
        print("subnet deletion error")
    if n_network:
        conn.network.delete_network(n_network)
        print("network deleted")
    else:
        print("network deletion error")
    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    n_webserver = conn.compute.find_server('shinrl1-web')
    n_appserver = conn.compute.find_server('shinrl1-app')
    n_dbserver = conn.compute.find_server('shinrl1-db')

    n_webserver = conn.compute.get_server(n_webserver)
    n_appserver = conn.compute.get_server(n_appserver)
    n_dbserver = conn.compute.get_server(n_dbserver)

    web_ip_address = n_webserver.addresses['shinrl1-net'][0]["addr"] 
    n_webname = n_webserver.name
    n_webstatus = n_webserver.status
    app_ip_address = n_appserver.addresses['shinrl1-net'][0]["addr"] 
    n_appname = n_appserver.name
    n_appstatus = n_appserver.status
    db_ip_address = n_dbserver.addresses['shinrl1-net'][0]["addr"] 
    n_dbname = n_dbserver.name
    n_dbstatus = n_dbserver.status
    if n_webserver:
        status = "%s is %s and has the ip address %s"%(n_webname, n_webstatus, web_ip_address)
        print(status)
    else:
        status = "%s cannnot be found"%(n_webserver)
        print(status)
    if n_appserver:
        status = "%s is %s and has the ip address %s"%(n_appname, n_appstatus, app_ip_address)
        print(status)
    else:
        status = "%s cannnot be found"%(n_appserver)
        print(status)
    if n_dbserver:
        status = "%s is %s and has the ip address %s"%(n_dbname, n_dbstatus, db_ip_address)
        print(status)
    else:
        status = "%s cannnot be found"%(n_dbserver)
        print(status)
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
