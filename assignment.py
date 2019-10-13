#Adam Valentine -- Virtulalization, Assmnt-2

import argparse
import openstack
from pprint import pprint
import time


# Variables with resource names
IMAGE = 'ubuntu-minimal-16.04-x86_64'  
FLAVOUR = 'c1.c1r1'
NETWORK =  'kiselv1-net' 
SUBNET = 'kiselv1-subnet'
SUBNET_IP = '192.168.50.0/24'
ROUTER = 'kiselv1-rtr'
PUBLIC_NET = 'public-net'
KEYPAIR = 'kiselv1-key'  # ---> Location: [nz_wlg_2] 
SERVER_NAMES = ['kiselv1-web', 'kiselv1-app', 'kiselv1-db']
SECURITY_GROUP = 'assignment2'

#Create connection object
conn = openstack.connect(cloud_name='openstack')


def create():
  ''' Create a set of Openstack resources '''  
  image = conn.compute.find_image(IMAGE)
  flavour = conn.compute.find_flavor(FLAVOUR)
  keypair = conn.compute.find_keypair(KEYPAIR)
  security_group = conn.network.find_security_group(SECURITY_GROUP)

  #---Network:
  print('-'*10  )
  print("Creating Network ", NETWORK, "  ...")  
  print('-'*10  )
  my_network = conn.network.find_network(NETWORK) 
  #Check if the Network already exists  
  if my_network is None: # If Network does Not Exist --> create it
    my_network = conn.network.create_network(name=NETWORK)
    print('-'*10  )
    print("Network ", NETWORK, " has been created successfully!")
  else:  
    print('-'*10  )	
    print("Network ", NETWORK, " is already exists !")    
  
  #---Subnet:
  print('-'*10  )
  print("Creating Subnet ", SUBNET, "  ...")  
  my_subnet = conn.network.find_subnet(SUBNET)
  #Check if the Subnet already exists   
  if my_subnet is None: # If Subnet does Not Exist --> create it
    my_subnet = conn.network.create_subnet(name=SUBNET, network_id = my_network.id, cidr=SUBNET_IP, ip_version='4')   	
    print('-'*10  )	
    print("Subnet ", SUBNET, " has been created successfully!")
  else:  
    print('-'*10  )	
    print("Subnet ", SUBNET, " is already exists !")

  #---Router:
  print('-'*10  )
  print("Creating Router ", ROUTER, "  ...")  
  my_pubnet = conn.network.find_network(PUBLIC_NET)
  if my_pubnet is None: print("Network ", PUBLIC_NET, " does not exists !")
  my_router = conn.network.find_router(ROUTER)
  if my_router is None and my_pubnet is not None: # If Router does Not Exist --> create it {also check that "my_pubnet" exists}
    my_router = conn.network.create_router(name=ROUTER, external_gateway_info={"network_id": my_pubnet.id})
    conn.network.add_interface_to_router(router=my_router, subnet_id=my_subnet.id)
    print('-'*10  )
    # -------------	
    print('-'*10  )
    print("Router ", ROUTER, " has been created successfully!")
  else:  
    print('-'*10  )	
    print("Router ", ROUTER, " is already exists !")	

  #---Servers:
  print('-'*10  )
  for serv_name in SERVER_NAMES: 
    if security_group is None: print("Warning: Security Group  ", SECURITY_GROUP, " does not exists! ", "Can't create servers!")
    if conn.compute.find_server(serv_name) is None and security_group is not None: # If server does Not Exist --> create it {also check that "security_group" exists}	
      print("Creating Server ", serv_name, "  ...")
      new_server = conn.compute.create_server(name=serv_name, image_id=image.id, flavor_id=flavour.id, networks=[{"uuid": my_network.id}], key_name=keypair.name, security_group=[{"sgid": security_group.id}])  
      new_server = conn.compute.wait_for_server(new_server)	
      if serv_name == "kiselv1-web":
        #---Creating Floating IP address :
        print('-'*10  )
        print("Creating Floating IP address for ", serv_name, "  ...") 
        # Accessing network (i.e. my_pubnet) and getting an "ip address" from it:
        my_floating_ip = conn.network.create_ip(floating_network_id=my_pubnet.id)
        # Now associate the address with the server
        conn.compute.add_floating_ip_to_server(new_server, my_floating_ip.floating_ip_address)
        print('-'*10  )
        print("Floating IP for ", serv_name, " has been created successfully!")
        print('-'*10  )
      print('='*10  )
      print("Creation of ", serv_name, " has COMPLETE successfully!")		
    else:
      print('='*10  )
      print("Server ", serv_name, " is already exists !")  
  

def run():
  ''' Start  a set of Openstack virtual machines
  if they are not already running.
  '''
  #---Start Servers: 
  print('-'*10  )
  print("Starting Servers ", "  ...")  
  for serv_name in SERVER_NAMES:
    print("Starting server: ", serv_name, "  ...")
    serv = conn.compute.find_server(serv_name)	
    if serv is not None: # Check that server Exists 	
      serv = conn.compute.get_server(serv)
      if serv.status == "SHUTOFF":
        conn.compute.start_server(serv)
        print("Server ", serv_name, " has been started successfully!")
      else:
        print("Server ", serv_name, " is already running!")
    else:
      print("Warning: Can't start ", "Server ", serv_name, ", as it does not exist!")


def stop():
  ''' Stop  a set of Openstack virtual machines
  if they are running.
  '''
  #---Stop Servers: 
  print('-'*10  )
  print("Stopping Servers ", "  ...")  
  for serv_name in SERVER_NAMES:
    print("Stopping server: ", serv_name, "  ...")
    serv = conn.compute.find_server(serv_name)	
    if serv is not None: # Check that server Exists 	
      serv = conn.compute.get_server(serv)
      if serv.status == "ACTIVE":
        conn.compute.stop_server(serv)
        print("Server ", serv_name, " has been stopped successfully!")
      else:
        print("Server ", serv_name, " is already stopped!")
    else:
      print("Warning: Can't stop ", "Server ", serv_name, ", as it does not exist!")  


def destroy():
  ''' Tear down the set of Openstack resources 
  produced by the create action
  '''  
  my_network = conn.network.find_network(NETWORK)    
  
  #---Delete Server: 
  print('-'*10  )
  print("Deleting Servers ", "  ...")  
  for serv_name in SERVER_NAMES:
    serv = conn.compute.find_server(serv_name)	
    if serv is not None: # Check that server Exists 	
      print("Deleting Server ", serv_name, "  ...")
      conn.compute.delete_server(serv)
      time.sleep(30)	  
      print('-'*10  )
      print("Server ", serv_name, " has been deleted successfully!")
    else:
      print("Server ", serv_name, " does not exists !")
      
  #---Delete Floating IP address:
  print('-'*10  )
  print("Deleting Floating IP ....")   
  while conn.network.find_available_ip() is not None:
      conn.network.delete_ip(conn.network.find_available_ip())
      print("Floating IP ", " has been deleted successfully!") 

  #---Delete Router:
  print("Deleting Router ", ROUTER, "  ...")
  my_router = conn.network.find_router(ROUTER)
  if my_router is not None: 
    conn.network.remove_interface_from_router(router=my_router, subnet_id=my_network.subnet_ids[0])
    conn.network.delete_router(my_router.id) #delete_router	
    print("Router ", ROUTER, " has been deleted successfully!")
  else:
    print("No Router found/deleted.")
  
  #---Delete Network and its subnets:
  print("Deleting Network ", NETWORK, "  ...")
  if my_network is not None:  
    for net_subnet in my_network.subnet_ids:
      my_subnet = conn.network.find_subnet(net_subnet)
      conn.network.delete_subnet(net_subnet)#, ignore_missing=False)
      if my_subnet is not None: print("Subnet ", str(my_subnet.name), " has been deleted successfully!")		
    conn.network.delete_network(my_network)#, ignore_missing=False) 
    print("Network ", NETWORK, " has been deleted successfully!")
  else:
    print("No Network found/deleted.")	
  #-----
  print('-'*10  )   
  print("All Resources Removed Successfully!")	


def status():
  ''' Print a status report on the OpenStack
  virtual machines created by the create action.
  '''
  #---Get Status of Servers: 
  print('-'*10  )
  print("Getting Status of Servers ", "  ...")  
  for serv_name in SERVER_NAMES:
    print('-'*10  )
    print("Getting Status of server: ", serv_name, "  ...")
    serv = conn.compute.find_server(serv_name)	
    if serv is not None:# Check that server Exists 		
      serv = conn.compute.get_server(serv)
      print("Server state of", serv_name, " --> ", str(serv.status))
      serv_ip_address = serv.addresses[NETWORK][0]["addr"]
      if serv_ip_address is None:
        print("Server ", serv_name, " IP address:", "not found")
      else:
        print("Server ", serv_name, " IP address:", str(serv_ip_address))		
    else:
      print("Can't get status --> ", "Server ", serv_name, ", does not exist!")



# =============================


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

	
	
# ============================= END





