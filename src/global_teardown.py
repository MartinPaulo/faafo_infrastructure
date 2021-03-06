from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.common.exceptions import BaseHTTPError
import time

__author__ = 'martinpaulo'

try:
    import configparser
except ImportError:
    import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('faafo.cfg')

auth_username = config.get('Connection', 'auth_username')
auth_password = config.get('Connection', 'auth_password')
auth_url = config.get('Connection', 'auth_url')
project_name = config.get('Connection', 'project_name')
region_name = config.get('Connection', 'region_name')

provider = get_driver(Provider.OPENSTACK)
conn = provider(auth_username,
                auth_password,
                ex_tenant_name=project_name,
                ex_force_auth_url=auth_url,
                ex_force_service_name='Compute Service',
                ex_force_auth_version='2.0_password',
                ex_force_service_region=region_name)


def delete_instance(instance_name):
    print('Checking for existing instance named {}...'.format(instance_name))
    for node in conn.list_nodes():
        if node.name == instance_name:
            print('Deleting instance '.format(node.name))
            conn.destroy_node(node)
            # wait for the node to be deleted before continuing
            found = True
            while found:
                found = False
                for a_node in conn.list_nodes():
                    if a_node.uuid == node.uuid:
                        found = True
                        break
                if found:
                    print('.')
                    time.sleep(5)
            break


def delete_security_group(security_group_name):
    print('Checking for existing security group {}...'.format(security_group_name))
    for security_group in conn.ex_list_security_groups():
        if security_group.name == security_group_name:
            print('Deleting security Group {}'.format(security_group.name))
            conn.ex_delete_security_group(security_group)


# prints the contents of a dictionary or list, even if they are nested
def dump(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print k
                dump(v)
            else:
                print '%s : %s' % (k, v)
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dump(v)
            else:
                print v
    else:
        print obj

images = conn.list_nodes()
for instance in images:
    print('Found instance named {}...'.format(instance.name))
    # dump(instance.extra)
    # the image id's of the two images I created for the event...
    if instance.extra['imageId'] in ('b82958dc-4071-41ab-978e-fc16d4767bf5', '778e7b2e-4e67-44eb-9565-9c920e236dfd'):
        print('Will delete {} '.format(instance.name))
        delete_instance(instance.name)

security_groups = conn.ex_list_security_groups()
for sg in security_groups:
    try:
        delete_security_group(sg.name)
    except BaseHTTPError as e:
        print('Could not delete {}'.format(sg.name))
