import argparse
import openstack

def create():
    #Create network
	openstack network create --internal 'andejt1-net'
	#Create subnet
	openstack subnet create --network andekt1-net --subnet-range 192.168.50.0/24 andejt1-subnet
	#Create FloatingIP
	 openstack floating ip create andejt1-net
    #Create router
	openstack router create andejt1-router
	openstack router add subnet andejt1-router andejt1-subnet
	openstack router set --external-gateway public-net andejt1-router
	#Create server andejt1-web
	openstack server create --image ubuntu-minimal-16.04-x86_64 \
							--flavor c1.c1r1 \
							--name andejt1-web \
							andejt1-server
	#Create server andejt1-app
	openstack server create --image ubuntu-minimal-16.04-x86_64 \
							--flavor c1.c1r1 \
							--name andejt1-app \
							andejt1-server						
	#Create server andejt1-db
	openstack server create --image ubuntu-minimal-16.04-x86_64 \
							--flavor c1.c1r1 \
							--name andejt1-db \
							andejt1-server		
    pass

def run():
    #Runs all currently stopped or unactive servers
    openstack server start andejt1-web
	openstack server start andejt1-app
	openstack server start andejt1-db
    pass

def stop():
    #Stops all currently running servers
	openstack server stop andejt1-web
	openstack server stop andejt1-app
	openstack server stop andejt1-db
    pass

def destroy():
    #Removes everything created in the create function
    openstack server delete andejt1-web
	openstack server delete andejt1-app
	openstack server delete andejt1-db
	openstack router remove subnet andejt1-router andejt1-subnet
	openstack router delete andejt1-router
	openstack router delete andejt1-subnet
	openstack network delete andejt1-net
    pass

def status():
    #Displays diagnostics of each server
    openstack server show --diagnostics andejt1-web
	openstack server show --diagnostics andejt1-app
	openstack server show --diagnostics andejt1-db
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
