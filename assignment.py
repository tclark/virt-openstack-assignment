import argparse
import openstack
conn = openstack.connect(cloud_name='openstack')

# I ran it using modules because I thought that way you can run the different functions seperately
# The create, run, stop, destroy and status functions are created under modules.
# You can run each function by running python assignment.py <function> eg: create...
def create():
    from modules.create import create

def run():
    from modules.run import run

def stop():
    from modules.stop import stop

def destroy():
    from modules.destroy import destroy

def status():
    from modules.status import status
    


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
