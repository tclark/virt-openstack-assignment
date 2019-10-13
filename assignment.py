#!/usr/bin/env python

'''
Simple Script Written in Python to Create, Destroy, Run, Stop and Show the 
    status of servers using openstack!

@author James McKenzie
@date October 2019
@usage ./assignment [-h] [create, stop, run, destroy, status]
@lang python 3.7 (Perl version not working)


Known Bugs:
    Creating a server when its already created will throw an error regarding
    IP's as there is already a floating Ip on the port. I would fix this with
    a try catch loop, however, I was not able to contain the error correctly

Lacked Features:
    Any Packaging System
    OS PATH/source Control

To-Do
    Fix bug Regarding Double Creation
    Extract the Constants section to a seperate file, and use grep to collect

This code is ANSI Width compliant, and follows PEP8 (Mostly)
This Code was written under GNU GPL3
'''



import argparse
import openstack


os_connect = openstack.connect(cloud_name='openstack')
# Constants that will be used throughout the script
# Kept here to be changed easily at the users whim
IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOR = 'c1.c1r1'
KEYPAIR = 'mckeja4-key'
SUBNET = 'mckeja4-subnet'
NETWORK = 'mckeja4-net'
ROUTER = 'mckeja4-router'
SECURITY_GROUP = 'assignment2'
PUBNET_NAME = 'public-net'
SERVER_NAMES = ['mckeja4-web', 'mckeja4-app', 'mckeja4-db']

def create():
    #I have prefaced the Openstack ???Objects/Structs??? with OS
    os_image = os_connect.compute.find_image(IMAGE)
    os_flavor = os_connect.compute.find_flavor(FLAVOR)
    os_keypair = os_connect.compute.find_keypair(KEYPAIR)
    os_public_net = os_connect.network.find_network(PUBNET_NAME)
    os_security_group = os_connect.network.find_security_group(SECURITY_GROUP)
    os_network = os_connect.network.find_network(NETWORK)
    
    
    if os_network != None:
        print('%s already exists! skipping...' % NETWORK)
        
    else:
        print('Creating %s '% NETWORK)
        os_network = os_connect.network.create_network(name=NETWORK)

    os_subnet = os_connect.network.find_subnet(SUBNET)
    if os_subnet != None:
        print('%s already exists! skipping... '% SUBNET)
    else:
        print('Creating %s ' % SUBNET)
        os_subnet = os_connect.network.create_subnet(name=SUBNET,
                                            cidr='192.168.50.0/24',
                                            ip_version=4,
                                            network_id=os_network.id)

    os_router = os_connect.network.find_router(ROUTER)
    if os_router != None:
        print('%s already exists! skipping... ' % ROUTER)
    else:
        print('Creating %s '  % ROUTER)
        ext = {'network_id': os_public_net.id}
        os_router = os_connect.network.create_router(name=ROUTER,
                                            external_gateway_info=ext)
        print('Creating interface for %s' % SUBNET)
        os_connect.network.add_interface_to_router(os_router, os_subnet.id)

    for server in SERVER_NAMES:
        s = os_connect.compute.find_server(server)
        if s != None:
            print('%s already exists! skipping...' % server)
        else:
            print('Creating %s' % server)
            s = os_connect.compute.create_server(name=server,
                                           image_id=os_image.id,
                                           flavor_id=os_flavor.id,
                                           key_name=os_keypair.name,
                                           networks=[{'uuid': os_network.id}],
                                           security_groups=[os_security_group])

    web = os_connect.compute.find_server('mckeja4-web')
    web = os_connect.compute.get_server(web.id)
    os_connect.compute.wait_for_server(web)
 
    #Creates a list of avalible Floating IPS
    floatingips = []
    for net in web.addresses:
        for a in web.addresses[net]:
            addrs = []
            if a['OS-EXT-IPS:type'] == 'floating':
                addrs.append(a['addr'])
        floatingips.extend(addrs)
    #Closes the program if no floating IPS avaliable
    if floatingips.__len__ == 0:
        print("There are no floating ips avalible")
        exit

    print('Creating floating IP address for mckeja4-web... ', end='')
    #Grabbing one of the IPs
    web_ip = os_connect.network.create_ip(floating_network_id=os_public_net.id)
    print('Got IP:', web_ip.floating_ip_address)
    #Assigning said IP
    print('Assigning address to mckeja4-web')
    os_connect.compute.add_floating_ip_to_server(web,
                                           web_ip.floating_ip_address)



def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    for server in SERVER_NAMES:
        s = os_connect.compute.find_server(server)
        if s == None:
            print(server, 'not found! skipping...')
        else:
            s = os_connect.compute.get_server(s)
            print('Starting %s... ' % server, end='')
            try:
                os_connect.compute.start_server(s.id)
            except openstack.exceptions.ConflictException:
                print('Currently Running!, skipping...')
            else:
                os_connect.compute.wait_for_server(s)
                print('OK')


def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''

    for server in SERVER_NAMES:
        s = os_connect.compute.find_server(server)
        if s == None:
            print('%s wasn\'t found! skipping...' % server)
        else:
            s = os_connect.compute.get_server(s.id)
            print('Shutting off %s... ' % server, end='')
            try:
                os_connect.compute.stop_server(s.id)
            except openstack.exceptions.ConflictException:
                print('%s was already shut off! skipping...' % server)
            else:
                os_connect.compute.wait_for_server(s, status='SHUTOFF')
                print('OK')


def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    # THIS IS NOT A SAFE DESTROY METHOD AND IS MAINLY WRITTEN TO BE
    # SCRIPTABLE WITH NO ADDITIONAL INPUT FROM THE USER
    # PLEASE EXERCISE CAUTION WHEN USING THIS
    os_subnet = os_connect.network.find_subnet(SUBNET)
    for server in SERVER_NAMES:
        s = os_connect.compute.find_server(server)
        if s != None:
            s = os_connect.compute.get_server(s)
            floatingips = []
            for net in s.addresses:
                for addr in s.addresses[net]:
                    addrs = []
                    if addr['OS-EXT-IPS:type'] == 'floating':
                        addrs.append(addr['addr'])
                floatingips.extend(addrs)

            for ip in floatingips:
                os_addr = os_connect.network.find_ip(ip)
                print('Releasing floating IP', ip)
                os_connect.network.delete_ip(os_addr)
            print('Deleting', server)
            os_connect.compute.delete_server(s, ignore_missing=True)
            print('Waiting for %s to be deleted' % server)
            while s:
                s = os_connect.compute.find_server(server)
        else:
            print('Can\'t find %s! skipping...' % server)
    os_router = os_connect.network.find_router(ROUTER)
    if os_router:
        print('Deleting interface for', SUBNET)
        os_connect.network.remove_interface_from_router(os_router, os_subnet.id)
        print('Deleting', ROUTER)
        os_connect.network.delete_router(os_router, ignore_missing=True)
    else:
        print('Can\'t to find %s! skipping...' % ROUTER)

    # Delete network if it exists.
    os_network = os_connect.network.find_network(NETWORK)
    if os_network:
        print('Deleting', SUBNET)
        os_connect.network.delete_subnet(os_subnet, ignore_missing=True)
        print('Deleting', NETWORK)
        os_connect.network.delete_network(os_network, ignore_missing=True)
    else:
        print('Can\'t find %s! skipping...' % NETWORK)


def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    servers = []
    # Get info for  servers.
    for name in SERVER_NAMES:
        print('Getting status of %s...' % name , end=' ')
        s = os_connect.compute.find_server(name)
        # Get full server info.
        if s:
            s = os_connect.compute.get_server(s.id)
            servers.append(s)
            print('OK')
        else:
            print('NOT FOUND')

    # Display status of known and found servers.
    for server in servers:
        print('\n%s: %s' % server.name, server.status)
        iplist = []
        for net in server.addresses:
            for a in server.addresses[net]:
                iplist.append(a['addr'])
        if iplist:
            print('IP\'s:')
            for i in iplist:
                print(i)
        else:
            print('No IP\'s were found!')



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
