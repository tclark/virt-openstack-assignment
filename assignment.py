import argparse
import openstack

conn = openstack.connect(cloud='openstack', region_name='nz-hlz-1')

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
