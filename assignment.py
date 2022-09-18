import argparse
import openstack
import getpass
#openstack.enable_logging()
conn = openstack.connect(cloud_name='openstack', region_name='nz-hlz-1')

IMAGE='ubuntu-minimal-22.04-x86_64'
FLAVOUR='c1.c1r1'
PRIVATE='private-net'
PUBLIC='public-net'
KEYPAIR='openstackkey'
USER='leggtc1'
SECURITYGROUP='assignment2'

def verify_create_keypair():
    keypair = conn.compute.find_keypair(KEYPAIR)
    if not keypair:
        print("Create Key Pair:")
        keypair = conn.compute.create_keypair(name=KEYPAIR)
        print(keypair)
        try:
            os.mkdir(SSH_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e
        with open(PRIVATE_KEYPAIR_FILE, 'w') as f:
            f.write("%s" % keypair.private_key)
        os.chmod(PRIVATE_KEYPAIR_FILE, 0o400)
    return keypair

SYSVAR = {
  "keypair": verify_create_keypair(),
  "image_id": conn.compute.find_image(IMAGE).id,
  "flavour_id": conn.compute.find_flavor(FLAVOUR).id,
  "privatenet_id": conn.network.find_network(PRIVATE).id,
  "border_id": conn.network.find_network(PUBLIC).id,
  "security_group": conn.network.find_security_group(SECURITYGROUP),
  "server_names": [f'{USER}-web', f'{USER}-app',f'{USER}-db'],
  "router": f'{USER}-rtr',
  "net_name": f'{USER}-net',
  "net_addr": '192.168.50.0/24',
  "subnet": f'{USER}-subnet',
  "gateway": '192.168.50.1',
  "ipv": '4',
}

def get_current_network():
    network = conn.network.find_network(SYSVAR['net_name'])
    return network

def get_current_subnet():
    subnet = conn.network.find_subnet(SYSVAR['subnet'])
    return subnet

def get_current_router():
    router = conn.network.find_router(SYSVAR['router'])
    return router

def create_network():
    network = get_current_network()
    subnet = get_current_subnet()
    router = get_current_router()
    if(network is None):
        print(f'\nCreating Network:\t{SYSVAR["net_name"]}')
        try:
            network = conn.network.create_network(name=SYSVAR['net_name'])
            print(f'Network {SYSVAR["net_name"]} created')
            print(f'Network ID: {network.id}')
        except:
            print(f'Error: {SYSVAR["net_name"]} creation failed')
    else:
        print(f'\n{SYSVAR["net_name"]}\tAlready Exists.')
    if(subnet is None):
        print(f'\nCreating Subnet\t{SYSVAR["subnet"]}')
        try:
            subnet = conn.network.create_subnet(name=SYSVAR['subnet'], 
            network_id=network.id,ip_version=SYSVAR['ipv'], cidr=SYSVAR['net_addr'], gateway_ip=SYSVAR['gateway']) 
            print(f'Subnet {SYSVAR["subnet"]} Created.')
            print(f'Subnet ID: {subnet.id}')
        except:
            print(f'Error: {SYSVAR["subnet"]} Creation Failed')
    else:
        print(f'\n{SYSVAR["subnet"]}\tAlready Exists.')
    if(router is None):
        print(f'\nCreating Router\t{SYSVAR["router"]}')
        try:
            router = conn.network.create_router(
                name=SYSVAR['router'],external_gateway_info={"network_id": SYSVAR['border_id']})
            print(f'Router {SYSVAR["router"]} Created')
            print(f'Router ID: {router.id}')
        except:
            print(f'Error: {SYSVAR["router"]} Creation Failed.')
        print(f'\nAdding Port to Router:\t{SYSVAR["router"]}')
        router = conn.network.add_interface_to_router(router,subnet_id=subnet.id)
        print(f'Added Port ID:\t{router["port_id"]}')
    else:
        print(f'\n{SYSVAR["router"]}\tAlready Exists.')

def get_current_servers():
    servers = {
        f'{USER}-web': conn.compute.find_server(f'{USER}-web', ignore_missing=True),
        f'{USER}-app': conn.compute.find_server(f'{USER}-app', ignore_missing=True),
        f'{USER}-db': conn.compute.find_server(f'{USER}-db', ignore_missing=True)
    }
    return servers

def delete_network():
    print(f'\nDeleting Network: {SYSVAR["net_name"]}\n')
    network = get_current_network()
    subnet = get_current_subnet()
    router = get_current_router()
    ports = None
    try:
        ports = conn.network.ports(network_id=network.id,subnet_id=subnet.id,ip_address=SYSVAR['gateway'])
        if(ports is not None):
            for port in ports:
                if(port.fixed_ips[0]['ip_address'] == SYSVAR['gateway']):
                    conn.network.remove_interface_from_router(router,subnet_id=subnet.id,port_id=port.id)
                else:
                    conn.network.delete_port(port.id, ignore_missing=True)
    except:
        print(f'Network {SYSVAR["net_name"]}: Does Not Exist/Cannot Be Deleted\n')
    if(subnet is not None):
        res = conn.network.delete_subnet(subnet, ignore_missing=True)
        print(f'Subnet: {SYSVAR["subnet"]} Has Been Deleted.')
    if(router is not None):
        conn.network.delete_router(router.id, ignore_missing=True)
        print(f'Router: {SYSVAR["router"]} Has Been Deleted.')
    if(network is not None):
        conn.network.delete_network(network, ignore_missing=True)
        print(f'Network: {SYSVAR["net_name"]} Has Been Deleted.')

def create_servers():
    network = get_current_network()
    if(network is None):
        print('\nCreating Servers........')
    current_servers = get_current_servers()
    for VM, state in current_servers.items():
        if(state is None):
            print(f'\nCreating New Server Instance: {VM}')
            newvm = conn.compute.create_server(name=VM, image_id=SYSVAR['image_id'], flavor_id=SYSVAR['flavour_id'], networks=[{'uuid': network.id}], 
                key_name=SYSVAR['keypair'].name)
            newvm = conn.compute.wait_for_server(newvm)
            conn.compute.add_security_group_to_server(newvm, SYSVAR['security_group'])
            print(f'\tSuccessfully Created: {newvm.name}')
            print(f'Server ID:\t{newvm.id}')
            print(f'Status:\t\t{newvm.status}\nKey Name:\t{newvm.key_name}\nZone:\t\t{newvm.location.zone}')
            print(f'\nGenerating New Public IP For {VM}')
            vmip = conn.network.create_ip(floating_network_id=SYSVAR['border_id'])
            conn.compute.add_floating_ip_to_server(newvm, vmip.floating_ip_address)
            vm = conn.compute.get_server(newvm.id)
            print(f'Public IP:\t{vm.addresses[SYSVAR["net_name"]][1]["addr"]}')
            print(f'Private IP:\t{vm.addresses[SYSVAR["net_name"]][0]["addr"]}')
            print(f'Security Group(s):')
            for group in vm.security_groups:
                print(f'\t{group["name"]}')
        else:
            print(f'\n{VM}\tAlready Exists.')
    return

def delete_current_ips():
    print('\nDeleting IPs.......\n')
    servers = get_current_servers()
    try:
        for VM, server in servers.items():
            if(server is not None):
                xserver = conn.compute.get_server(server.id)
                ip = xserver['addresses'][SYSVAR['net_name']][1]['addr']
                print(f'\nRemoving IP: {ip} From {VM}')
                try:
                    conn.compute.remove_floating_ip_from_server(xserver, ip)
                    print(f'\t\tIP: {ip} Removed From {VM}')
                except:
                    print(f'\t\tError removing IP {ip}')
                print(f'Removing IP: {ip} From {SYSVAR["net_name"]}')
                try:
                    netip = conn.network.find_ip(ip)
                    conn.network.delete_ip(netip)
                    print(f'\t\tIP {ip} Removed From {SYSVAR["net_name"]}')
                except:
                    print(f'Error deleting IP {ip}')
            else:
                print(f'No IP Address Assigned To:\t{VM}')
    except:
        print(f'\nAll IPs for {SYSVAR["net_name"]} have been deleted.\n')

def delete_all_servers():
    print('\nDeleting Servers.......\n')
    current_servers = get_current_servers()
    for server, state in current_servers.items():
        if(state is not None):
            try:
                vm = conn.compute.delete_server(state, ignore_missing=True)
                print(f'{server}, has been deleted.')
            except:
                print(f'An Error Occured While Deleting Server: {server}')
        else:
            print(f'Server Unavailable To Delete:\t{server}')

def get_network_status():
    print(f'\nCollecting Data for Network: {SYSVAR["net_name"]}.......')
    network = get_current_network()
    if(network is not None):
        print(f'Network Name:\t{network.name}')
        print(f'Network Status:\t{network.status}')
        print(f'Created:\t{network["created_at"]}')
        print(f'Updated:\t{network["updated_at"]}')
        print(f'Zone:\t\t{network["availability_zones"][0]}')
    else:
        print(f'\t{SYSVAR["net_name"]} Does Not Exist.')

def get_router_status():
    print(f'\nCollecting Data for Router: {SYSVAR["router"]}.......')
    router = get_current_router()
    if(router is not None):
        print(f'Router Name\t{router.name}')
        print(f'outer Status:\t{router.status}')
        print(f'Public IP\t{router.external_gateway_info["external_fixed_ips"][0]["ip_address"]}')
        print(f'Zone:\t\t{router.availability_zones[0]}')
        print(f'Created\t\t{router["created_at"]}')
        print(f'Updated:\t{router["updated_at"]}')
    else:
        print(f'\t{SYSVAR["router"]} Does Not Exist')

def get_subnet_status():
    print(f'\nCollecting Data for Subnet: {SYSVAR["subnet"]}.......')
    subnet = get_current_subnet()
    if(subnet is not None):
        print(f'Subnet Name \t{subnet.name}')
        print(f'Gateway:\t{subnet["gateway_ip"]}')
        print(f'Network Range:\tStart:\t{subnet["allocation_pools"][0]["start"]}\n\t\tEnd:\t{subnet["allocation_pools"][0]["end"]}')
        print(f'DHCP Enabled:\t{subnet["enable_dhcp"]}')
        print(f'Created\t\t{subnet["created_at"]}')
        print(f'Updated:\t{subnet["updated_at"]}')
    else:
        print(f'\t{SYSVAR["subnet"]} Does Not Exist')

def get_servers_status():
    print('\nCollecting Server Data.......')
    allserver = get_current_servers()
    if(allserver is not None):
        for server_name, xserver in allserver.items():
            if(xserver is not None):
                res = conn.compute.get_server(xserver.id)
                print(f'\nServer:\t\t{server_name}')
                print(f'Status:\t\t{res.status}')
                print(f'Public IP:\t{res["addresses"][SYSVAR["net_name"]][1]["addr"]}')
                print(f'IP Type:\t{res["addresses"][SYSVAR["net_name"]][1]["OS-EXT-IPS:type"]}')
                print(f'Private IP:\t{res["addresses"][SYSVAR["net_name"]][0]["addr"]}')
                print(f'IP Type:\t{res["addresses"][SYSVAR["net_name"]][0]["OS-EXT-IPS:type"]}')
                print(f'Key Name:\t{res.key_name}')
                print(f'Region Zone:\t{res.location.region_name}')
                print('Security Group(s):')
                for group in res.security_groups:
                    print(f'\t\t{group["name"]}')
                print(f'Created:\t{res["created_at"]}')
                print(f'Updated:\t{res["updated_at"]}')
            else:
                print(f'\t{server_name} Does Not Exist')
                
def create():
    verify_create_keypair()
    create_network()
    create_servers()
    pass

def run():
    print(f'\nGetting Server Data......\n')
    servers = get_current_servers()
    for server_name, server in servers.items():
        if(server is not None):
            res = conn.compute.get_server(server.id)
            if(res.status == "SHUTOFF"):
                print(f'Starting Server:\t{server_name}')
                conn.compute.start_server(server.id)
            else:
                print(f'Server: {server_name}\tis already running.')
        else:
            print(f'Server Error:\n\t{server_name} is not currently unavailable/configured.')    
    pass

def stop():
    print(f'\nGetting Server Data......\n')
    servers = get_current_servers()
    for server_name, server in servers.items():
        if(server is not None):
            res = conn.compute.get_server(server.id)
            if(res.status == "ACTIVE"):
                print(f'Shutting Down Server: {server_name}')
                stat = conn.compute.stop_server(server.id)
            else:
                print(f'Server: {server_name}\thas already been stopped.')
        else:
            print(f'Server Error:\n\t{server_name} is not currently unavailable/configured.')    
    pass

def destroy():
    # 1. Disassociate and release the floating ip on each server
    delete_current_ips()
    # 2. Delete each server
    delete_all_servers()
    # 3. Delete the network, subnet, ports & router
    delete_network()
    pass

def status():
    get_servers_status()
    get_network_status()
    get_subnet_status()
    get_router_status()
    pass

### You should not modify anything below this line ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', help='One of "create", "run", "stop", "destroy", or "status"')
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
