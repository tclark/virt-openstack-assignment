import argparse
import openstack

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOR = 'c1.c1r1'
KEYPAIR = 'hayeska2-key'
SUBNET = 'hayeska2-subnet'
NETWORK = 'hayeska2-net'
ROUTER = 'hayeska2-router'
SECURITY_GROUP = 'assignment2'
PUBNET_NAME = 'public-net'
SERVER_NAMES = ['hayeska2-web', 'hayeska2-app', 'hayeska2-db']

conn = openstack.connect(cloud_name='openstack')

def create():
    ''' Create a set of Openstack resources '''
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
