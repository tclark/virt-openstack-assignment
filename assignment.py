import argparse
import openstack


conn = openstack.connect(cloud_name='openstack', region_name ='nz-hlz-1a')

for server in conn.compute.servers():
   # pprint(server)
    

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOR = 'c1.c1r1'
SECURITYGROUP = "assignment2"
KEYPAIR = 'chauw2key'
PUBLICNET = 'public-net'

cidr = '192.168.50.0/24'
NETWORK = 'chauw2-net'
SUBNET = 'chauw2-subnet'
ROUTER = 'chauw2-rtr'
ALLSERVERSLIST = ['chauw2-web','chauw2-app','chauw2-db']
#WEB-SERVER = 'chauw2-web'
#APP-SERVER = 'chauw2-app'
#DB-SERVER = 'chauw2-db'


# Create openstack rescore
#https://docs.openstack.org/openstacksdk/latest/user/guides/compute.html
image = conn.compute.find_image(IMAGE)
flavor  = conn.compute.find_flavor(FLAVOR)
public_network = conn.compute.find_network(PUBLICNET)
keypair = conn.compute.find_keypair(KEYPAIR)
security_group = conn.network.find_security_group(SECURITYGROUP)
publicnet = conn.network.find_network(PUBLICNET)


def create():
    ''' Create a set of Openstack resources '''
    # Find network
    print("Searching Network...")
    network = conn.network.find_network(NETWORK)
    if network is None:
         print('Creating', NETWORK)
        network = conn.network.create_network(name=NETWORK)
    else
        print(NETWORK, 'exists in the network')
         
    #Find Subnet
    subnet = conn.network.find_subnet(SUBNET)
      print("Searching Subnet...")
    if subnet is None:
       print('Creating', SUBNET)
      subnet = conn.network.create_subnet(name=SUBNET,network_id=network.id,cidr,ip_verison=4)
    else
        print(SUBNET, 'exists in the network')
    
   #Find Router
   #https://docs.catalystcloud.nz/first-instance/shade-sdk.html
   router = conn.network.find_router(ROUTER)
   if router is None
      print('Creating' , ROUTER)
      router = conn.network.create_router(name=ROUTER, external_gateway_info={ext_gateway_net_id=external_net.id)
   else
      print(ROUTER, 'exists in the network')
                                                                              
    # Find server
  
    print("Searching Server...") 
    '''
    if webserver = conn.compute.find_server(WEB-SERVER)
    if webser is None:
        print(WEB-SERVER ,'exist')
    else
    # create servers
       server = conn.compute.create_server(
        name=SERVER_NAME, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name)
    '''                                                                   
    for servername in ALLSERVERSLIST:
      ser = conn.compute.find_server(servername)
    if ser is None:
         print('Creating server', eachserver)
           ser = conn.compute.create_server() 
      else
      pint(eachserver, 'exists in the server')
                                                                             
                                                                              
    print("Waiting for the server to come up")
    server = conn.compute.wait_for_server(server)
      


    

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
  # NETWORK = 'chauw2-net'
  # SUBNET = 'chauw2-subnet'
   #ROUTER = 'chauw2-router'
               
      
   print("Delete Network:")
    example_network = conn.network.find_network(
        'openstacksdk-example-project-network')

    for example_subnet in example_network.subnet_ids:
        conn.network.delete_subnet(example_subnet, ignore_missing=False)
    conn.network.delete_network(example_network, ignore_missing=False) 
   
   
      
   drouter = conn.network.find_router(ROUTER)
   if router is not None:
      conn.network.delete_router
   else
      print(ROUETR + "does not exist")
                                         
                                           

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
