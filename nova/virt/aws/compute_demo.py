#!/usr/bin/env python
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# This example provides both a running script (invoke from command line)
# and an importable module one can play with in Interactive Mode.
#
# See docstrings for usage examples.
#

try:
    import secrets
except ImportError:
    secrets = None

import os.path
import sys

# Add parent dir of this file's dir to sys.path (OS-agnostically)
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__),
                                 os.path.pardir)))

from libcloud.common.types import InvalidCredsError
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeSize, NodeImage

import time
from pprint import pprint
import adapter
from libcloud.storage.base import Container, Object

def test_delete_snapshots():

    ACCESS_ID = 'AKIAJLGLIP7A3T3FB2PA'
    SECRET_KEY = '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'

    c_driver = adapter.Ec2Adapter(ACCESS_ID,SECRET_KEY,region='ap-southeast-1',secure=False)

    snapshot_list = c_driver.list_snapshots(owner='self')
    # snapshot_list = c_driver.list_snapshots(snapshot_ids=['snap-d6243038'])

    print len(snapshot_list)
    for ii in range(len(snapshot_list)-1,0,-1):
        print ii
        try:
            c_driver.destroy_volume_snapshot(snapshot_list[ii])
        except Exception as e:
            print e




def test_import():
    ACCESS_ID = 'AKIAJZ4GDBCM7KBFKVIQ'
    SECRET_KEY = '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'

    IMAGE_ID = 'ami-68d8e93a'
    SIZE_ID = 't2.micro'

    # cls = get_driver(Provider.EC2_AP_SOUTHEAST)
    # driver1 = cls(ACCESS_ID, SECRET_KEY, secure=False)

    driver = adapter.Ec2Adapter(ACCESS_ID,SECRET_KEY,region='ap-southeast-1',secure=False)
    s_driver = adapter.S3Adapter(ACCESS_ID,SECRET_KEY,region='ap-southeast-1',secure=False)

    task = driver.create_import_volume_task('wfbucketse','hostos-template-disk1.vmdk',
                              'VMDK', 2935714816, 50)

    while not task.is_completed():
        time.sleep(10)
        task = driver.get_task_info(task)


    print('sucess!')

def test_s3upload():
    ACCESS_ID = 'AKIAJZ4GDBCM7KBFKVIQ'
    SECRET_KEY = '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'

    IMAGE_ID = 'ami-68d8e93a'
    SIZE_ID = 't2.micro'

    s_driver = adapter.S3Adapter(ACCESS_ID,SECRET_KEY,region='ap-southeast-1',secure=False)

    container = Container(name='wfbucketse', extra={}, driver=s_driver)
    object_name = 'foo_test_stream_data1'
    extra = {'content_type': 'text/plain'}

    # with open('d:/wangfeng/vm-4b2bb3c5-a634-46df-9c33-5d8832f95b3f-disk-0.vmdk','rb') as f:
    #     obj = s_driver.upload_object_via_stream(container=container,
    #                                                object_name=object_name,
    #                                                iterator=f,
    #                                                extra=extra)

    obj = s_driver.get_object(container.name,object_name)
    s_driver.download_object(obj,'d:/wangfeng/s3test.vmdk')



    print('sucess!')

def test_aws():

    ACCESS_ID = 'AKIAJLGLIP7A3T3FB2PA'
    SECRET_KEY = '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'

    IMAGE_ID = 'ami-d06c5282'
    SIZE_ID = 't2.micro'

    cls = get_driver(Provider.EC2_AP_SOUTHEAST)
    driver1 = cls(ACCESS_ID, SECRET_KEY, secure=False)


    c_driver = adapter.Ec2Adapter(ACCESS_ID,SECRET_KEY,region='ap-southeast-1',secure=False)
    s_driver = adapter.S3Adapter(ACCESS_ID,SECRET_KEY,region='ap-southeast-1',secure=False)
    try:
        image = c_driver.get_image(IMAGE_ID)
    except Exception,e:
        e

    # sizes = driver.list_sizes()
    # nodes = driver.list_nodes()

    size = NodeSize(id=SIZE_ID, name=None, ram=None, disk=None, bandwidth=None,
                    price=None, driver=c_driver)
    # image = NodeImage(id=IMAGE_ID, name=None, driver=driver)

    try:
        c_driver.list_nodes('xxxxxxx')
    except Exception as e:
        print e

    node = c_driver.create_node(name='test-node', image=image, size=size)

    c_driver.destroy_node(node)
    # Here we allocate and associate an elastic IP
    elastic_ip = c_driver.ex_allocate_address()
    c_driver.ex_associate_address_with_node(node, elastic_ip)
    c_driver.list_nodes(ex_node_ids=['i-05febec9'])

    # When we are done with our elastic IP, we can disassociate from our
    # node, and release it
    c_driver.ex_disassociate_address(elastic_ip)
    c_driver.ex_release_address(elastic_ip)


    # task = driver.create_export_instance_task('i-7590e3b9', 'wfbucketse')
    #
    # while not task.is_completed():
    #     time.sleep(5)
    #     task = driver.get_task_info(task)

    # obj_key =  'foo_test_upload.vmdk'
    #
    #
    #     # c) download from s3
    # conv_dir = '%s\%s' % ('d:','wangfeng')
    #
    # org_full_name = 'd:\wangfeng\s3download.vmdk'
    # obj = s_driver.get_object('wfbucketse',obj_key)

    # write_file_handler = open(org_full_name, "wb")
    # stream =  s_driver.download_object_as_stream(obj,chunk_size=1024*16)
    # ii =0
    # while(True):
    #     try:
    #         data =stream.next()
    #         write_file_handler.write(data)
    #         write_file_handler.flush()
    #         ii += 1
    #         print ii
    #     except StopIteration:
    #         break
    #     except:
    #         write_file_handler.close()
    #         break
    #
    # write_file_handler.close()


    # with open(org_full_name, 'wb') as f:
    #     ii = 0
    #     for chunk in s_driver.download_object_as_stream(obj,chunk_size=1024*16):
    #         if chunk: # filter out keep-alive new chunks
    #             f.write(chunk)
    #             f.flush()
    #             ii += 1
    #             print ii

    # s_driver.download_object(obj,conv_dir,overwrite_existing=True)


    # images = driver.list_images()
    # image = driver.get_image(IMAGE_ID)

    # size = [s for s in sizes if s.id == SIZE_ID][0]
    # image = [i for i in images if i.id == IMAGE_ID][0]

def get_demo_driver(provider_name='RACKSPACE', *args, **kwargs):
    """An easy way to play with a driver interactively.

    # Load credentials from secrets.py:
    >>> from compute_demo import get_demo_driver
    >>> driver = get_demo_driver('RACKSPACE')

    # Or, provide credentials:
    >>> from compute_demo import get_demo_driver
    >>> driver = get_demo_driver('RACKSPACE', 'username', 'api_key')
    # Note that these parameters vary by driver ^^^

    # Do things like the demo:
    >>> driver.load_nodes()
    >>> images = driver.load_images()
    >>> sizes = driver.load_sizes()

    # And maybe do more than that:
    >>> node = driver.create_node(
        ... name='my_first_node',
        ... image=images[0],
        ... size=sizes[0],
        ... )
    >>> node.destroy()
    """
    provider_name = provider_name.upper()

    DriverClass = get_driver(getattr(Provider, provider_name))

    if not args:
        args = getattr(secrets, provider_name + '_PARAMS', ())
    if not kwargs:
        kwargs = getattr(secrets, provider_name + '_KEYWORD_PARAMS', {})

    try:
        return DriverClass(*args, **kwargs)
    except InvalidCredsError:
        raise InvalidCredsError(
            'valid values should be put in secrets.py')

def main(argv):
    """Main Compute Demo

    When invoked from the command line, it will connect using secrets.py
    (see secrets.py-dist for instructions and examples), and perform the
    following tasks:

    - List current nodes
    - List available images (up to 10)
    - List available sizes (up to 10)
    """

    test_delete_snapshots()
    # test_aws()
    # import_test()
    # test_s3upload()

    # try:
    #     driver = get_demo_driver()
    # except InvalidCredsError:
    #     e = sys.exc_info()[1]
    #     print("Invalid Credentials: " + e.value)
    #     return 1
    #
    # try:
    #     print(">> Loading nodes...")
    #     pprint(driver.list_nodes())
    #
    #     print(">> Loading images... (showing up to 10)")
    #     pprint(driver.list_images()[:10])
    #
    #     print(">> Loading sizes... (showing up to 10)")
    #     pprint(driver.list_sizes()[:10])
    # except Exception:
    #     e = sys.exc_info()[1]
    #     print("A fatal error occurred: " + e)
    #     return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))

