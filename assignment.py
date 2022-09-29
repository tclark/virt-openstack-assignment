import argparse
import openstack
import time

def create():
    ''' Create a set of Openstack resources '''
    IMAGE = 'ubuntu-minimal-22.04-x86_64'
    FLAVOUR = 'c1.c1r1'
    KEYPAIR = 'ZachPepper-key'

    conn = openstack.connect(cloud_name='catalystcloud')

    network = conn.network.find_network('peppzg1-net')
    public_net = conn.network.find_network('public-net')


    if network is None:
        network = conn.network.create_network(name='peppzg1-net')
        print(network.name + " Network Created!")
    else:
        print("Network already exists!")


    subnet = conn.network.find_subnet('peppzg1-subnet')

    if subnet is None:
        subnet = conn.network.create_subnet(
            name = 'peppzg1-subnet',
            network_id = network.id,
            ip_version = '4',
            cidr = '192.168.50.0/24')
        print(subnet.name + " Subnet Created!")
    else:
        print("Subnet Already Exists!")

    router = conn.network.find_router('peppzg1-rtr')

    if router is None:
        router = conn.network.create_router(name = 'peppzg1-rtr', external_gateway_info={'network_id': public_net.id})
        conn.network.add_interface_to_router(router, subnet.id)
        print(router.name + " Router Created!")
    else:
        print("Router Already Exists!")

    image = conn.compute.find_image(IMAGE)
    flavour = conn.compute.find_flavor(FLAVOUR)
    keypair = conn.compute.find_keypair(KEYPAIR)

    web = conn.compute.find_server('peppzg1-web')

    if web is None:
        web = conn.compute.create_server(
            name = 'peppzg1-web', image_id=image.id, flavor_id=flavour.id,
            networks=[{"uuid": network.id}], key_name=keypair.name)

        web = conn.compute.wait_for_server(web)

        print(web.name + " Server Created!")
    else:
        print("Web Server Already Exists!")


    app = conn.compute.find_server('peppzg1-app')

    if app is None:
        app = conn.compute.create_server(
            name = 'peppzg1-app', image_id=image.id, flavor_id=flavour.id,
            networks=[{"uuid": network.id}], key_name=keypair.name)

        app = conn.compute.wait_for_server(app)
        print(app.name + " Server Created!")
    else:
        print("App Server Already Exists!")


    db = conn.compute.find_server('peppzg1-db')

    if db is None:
        db = conn.compute.create_server(
            name = 'peppzg1-db', image_id=image.id, flavor_id=flavour.id,
            networks=[{"uuid": network.id}], key_name=keypair.name)

        db = conn.compute.wait_for_server(db)
        print(db.name + " Server Created!")
    else:
        print("DB Server Already Exists")

    web = conn.compute.find_server('peppzg1-web')
    web = conn.compute.get_server(web.id)

    floatingIP = conn.network.find_ip(
        conn.compute.get_server(web.id).addresses["peppzg1-net"][1]['addr']
            )

    if floatingIP is None:
        floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
        conn.compute.add_floating_ip_to_server(web, floating_ip.floating_ip_address)
    else:
        print("Web server already has a floating IP associated to it")


    pass

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    conn = openstack.connect(cloud_name='catalystcloud')

    web = conn.compute.find_server('peppzg1-web')
    web = conn.compute.get_server(web.id)

    if web is None:
        print("Web Server Does Not Exist")
    elif web is not None and web.power_state == 1:
        print(web.name + " Server is Already Running!")
    else:
        conn.compute.start_server(web)
        print(web.name + " Server Has Started!")

    app = conn.compute.find_server('peppzg1-app')
    app = conn.compute.get_server(app.id)

    if app is None:
        print("App Server Does Not Exist")
    elif app is not None and app.power_state == 1:
        print(app.name + " Server is Already Running!")
    else:
        conn.compute.start_server(app)
        print(app.name + " Server Has Started!")

    db = conn.compute.find_server('peppzg1-db')
    db = conn.compute.get_server(db.id)

    if db is None:
        print("DB Server Does Not Exist")
    elif db is not None and db.power_state == 1:
        print(db.name + " Server is Already Running!")
    else:
        conn.compute.start_server(db)
        print(db.name + " Server Has Started!")


    pass

def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    conn = openstack.connect(cloud_name='catalystcloud')

    web = conn.compute.find_server('peppzg1-web')
    web = conn.compute.get_server(web.id)

    if web is None:
        print("Web Server Does Not Exist")
    elif web is not None and web.power_state == 1:
        conn.compute.stop_server(web)
        print(web.name + " Server Has Stopped!")
    else:
        print(web.name + " Server Has Already Stopped!")

    app = conn.compute.find_server('peppzg1-app')
    app = conn.compute.get_server(app.id)

    if app is None:
        print("App Server Does Not Exist")
    elif app is not None and app.power_state == 1:
        conn.compute.stop_server(app)
        print(app.name + " Server Has Stopped!")
    else:
        print(app.name + " Server Has Already Stopped!")

    db = conn.compute.find_server('peppzg1-db')
    db = conn.compute.get_server(db.id)

    if db is None:
        print("db Server Does Not Exist")
    elif db is not None and db.power_state == 1:
        conn.compute.stop_server(db)
        print(db.name + " Server Has Stopped!")
    else:
        print(db.name + " Server Has Already Stopped!")

    pass

def destroy():
    ''' Tear down the set of Openstack resources
    produced by the create action
    '''
    conn = openstack.connect(cloud_name='catalystcloud')

    if conn.compute.find_server('peppzg1-web') is None:
        print("")
    else:
        web = conn.compute.find_server('peppzg1-web')
        web = conn.compute.get_server(web.id)

        floatingIP = conn.network.find_ip(
            conn.compute.get_server(web.id).addresses["peppzg1-net"][1]['addr']
                )
        conn.network.delete_ip(floatingIP)
        print("Floating IP has been deleted from " + web.name)

        conn.compute.delete_server(web)
        print("Web Server has been Deleted!")

    if conn.compute.find_server('peppzg1-app') is None:
        print("")
    else:
        app = conn.compute.find_server('peppzg1-app')
        app = conn.compute.get_server(app.id)
        conn.compute.delete_server(app)
        print("App Server has been Deleted!")

    if conn.compute.find_server('peppzg1-db') is None:
        print("")
    else:
        db = conn.compute.find_server('peppzg1-db')
        db = conn.compute.get_server(db.id)
        conn.compute.delete_server(db)
        print("DB Server has been Deleted!")

    time.sleep(10)


    if conn.network.find_router('peppzg1-rtr') is None:
        print("")
    else:
        subnet = conn.network.find_subnet('peppzg1-subnet')
        router = conn.network.find_router('peppzg1-rtr')
        conn.network.remove_interface_from_router(router, subnet.id)
        conn.network.delete_router(router)
        print("Router has been Deleted!")


    if conn.network.find_subnet('peppzg1-subnet') is None:
        print("")
    else:
        subnet = conn.network.find_subnet('peppzg1-subnet')
        conn.network.delete_subnet(subnet, ignore_missing=False)
        print("Subnet has been Deleted!")

    if conn.network.find_network('peppzg1-net') is None:
        print("")
    else:
        network = conn.network.find_network('peppzg1-net')
        conn.network.delete_network(network, ignore_missing=False)
        print("Network has been Deleted!")

    pass

def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    conn = openstack.connect(cloud_name='catalystcloud')

    if conn.compute.find_server('peppzg1-web') is None:
        print("Web Server does not Exist!")
    else:
        web = conn.compute.find_server('peppzg1-web')
        web = conn.compute.get_server(web.id)

        print("Web Server:")
        print("Status: " + web.status)
        webnetlist = web.addresses["peppzg1-net"]
        webnetdict = webnetlist[0]
        print("IP Address: " + webnetdict["addr"])

        floatingIP = conn.compute.get_server(web.id).addresses["peppzg1-net"][1]['addr']
        print("Floating IP Address: " + floatingIP)


    print("")

    if conn.compute.find_server('peppzg1-app') is None:
        print("App Server does not Exist!")
    else:
        app = conn.compute.find_server('peppzg1-app')
        app = conn.compute.get_server(app.id)
        print("App Server:")
        print("Status: " + app.status)
        appnetlist = app.addresses["peppzg1-net"]
        appnetdict = appnetlist[0]
        print("IP Address: " + appnetdict["addr"])

    print("")

    if conn.compute.find_server('peppzg1-db') is None:
        print("DB Server does not Exist!")
    else:
        db = conn.compute.find_server('peppzg1-db')
        db = conn.compute.get_server(db.id)
        print("DB Server:")
        print("Status: " + db.status)
        dbnetlist = db.addresses["peppzg1-net"]
        dbnetdict = dbnetlist[0]
        print("IP Address: " + dbnetdict["addr"])

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
