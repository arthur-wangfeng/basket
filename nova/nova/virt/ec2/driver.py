from py4j.java_gateway import JavaGateway, GatewayClient
from nova import exception
from nova.i18n import _, _LW
from nova.openstack.common import jsonutils
from nova.openstack.common import log as logging
from nova.openstack.common import uuidutils
from nova.virt import driver
from oslo.config import cfg
from nova.compute import power_state
from nova import compute
from nova import network
from nova import volume


LOG = logging.getLogger(__name__)


class AwsEc2Driver(driver.ComputeDriver):
    """The EC2 java server"""

    aws_ec2_java_server = None
    VERSION = "1.0"

    def __init__(self, virtapi, scheme="https"):
        super(AwsEc2Driver, self).__init__(virtapi)
        self.aws_ec2_java_server = JavaGateway(GatewayClient(port=25535)).entry_point
        self.network_api = network.API()
        self.volume_api = volume.API()
        self.compute_api = compute.API(network_api=self.network_api,
                                       volume_api=self.volume_api)
        # record openstack instance-uuid to EC2 instance-id
        self.instances = {}
        # TODO: configure aws backend in openstack
        '''if (
            CONF.ec2.access_key is None or
            CONF.ec2.access_secret_key is None):
            raise Exception(_("Must specify access_key, access_secret_key"
                              "to use ec2.AwsEc2Driver"))'''
    def init_host(self, host):
        pass

    def list_instances(self):
        """List VM instances from all nodes."""
        # TODO: list instances from aws
        instances = []
        return instances

    def snapshot(self, context, instance, image_id, update_task_state):
        pass

    def set_bootable(self, instance, is_bootable):
        pass

    def set_admin_password(self, instance, new_pass):
        pass

    def spawn(self, context, instance, image_meta, injected_files,
              admin_password, network_info=None, block_device_info=None):
        """Create VM instance."""
        LOG.debug(_("image meta is:%s") % image_meta)
        ec2_image_id = self.aws_ec2_java_server.getImageIdFromName(
            image_meta['id'])
        LOG.debug(_("ec2 image id is:%s") % ec2_image_id)

        LOG.debug(_("instance is:%s") % instance)
        ec2_vm_name = instance['uuid']
        launch_result = self.aws_ec2_java_server.launchInstanceFromAMI(
            ec2_image_id, ec2_vm_name)

        LOG.debug("Instance is running %s" % instance)
        LOG.debug("launch result:%s, %s" % (launch_result['public-ip'],
                                            launch_result['instance-id']))
        # save ec2 instance id into cache
        self.instances[ec2_vm_name] = launch_result['instance-id']

    def attach_volume(self, context, connection_info, instance, mountpoint,
                      disk_bus=None, device_type=None, encryption=None):
        """Attach volume storage to VM instance."""
        openstack_volume_id = connection_info['data']['volume_id']
        LOG.info("attach ec2 volume")
        ec2_instance_id = self._get_ec2_instance_id(instance['uuid'])
        ec2_volume_id = self.aws_ec2_java_server.getVolumeIdFromName(
            openstack_volume_id)
        # TODO need to change device name
        ec2_rule = "/dev/sd"
        ec2_mountpoint = ec2_rule + mountpoint[-1]
        self.aws_ec2_java_server.attachVolumeToInstance(ec2_volume_id,
                                                        ec2_instance_id,
                                                        ec2_mountpoint)

    def get_available_resource(self, nodename):
        """Retrieve resource info.

        This method is called when nova-compute launches, and
        as part of a periodic task.

        :returns: dictionary describing resources

        """
        return {'vcpus': 32,
                'memory_mb': 164403,
                'local_gb': 5585,
                'vcpus_used': 0,
                'memory_mb_used': 69005,
                'local_gb_used': 3479,
                'hypervisor_type': 'vcloud',
                'hypervisor_version': 5005000,
                'hypervisor_hostname': nodename,
                'cpu_info': '{"model": ["Intel(R) Xeon(R) CPU E5-2670 0 @ 2.60GHz"], \
                "vendor": ["Huawei Technologies Co., Ltd."], \
                "topology": {"cores": 16, "threads": 32}}',
                'supported_instances': jsonutils.dumps(
                    [["i686", "ec2", "hvm"], ["x86_64", "vmware", "hvm"]]),
                'numa_topology': None,
                }
        
    def get_available_nodes(self, refresh=False):
        """Returns nodenames of all nodes managed by the compute service.

        This method is for multi compute-nodes support. If a driver supports
        multi compute-nodes, this method returns a list of nodenames managed
        by the service. Otherwise, this method should return
        [hypervisor_hostname].
        """
        return "aws-ec2-hypervisor" 

    def get_info(self, instance):
        ec2_instance_id = self._get_ec2_instance_id(instance['uuid'])

        if ec2_instance_id == 'None':
            return {'state': power_state.NOSTATE,
                'max_mem': 0,
                'mem': 0,
                'num_cpu': 1,
                'cpu_time': 0}

        ec2_instance_state = self.aws_ec2_java_server.\
            getInstanceStatus(ec2_instance_id)

        if ec2_instance_state == 'None':
            return {'state': power_state.NOSTATE,
                'max_mem': 0,
                'mem': 0,
                'num_cpu': 1,
                'cpu_time': 0}
        elif ec2_instance_state == 'running':
            return {'state': power_state.RUNNING,
                'max_mem': 0,
                'mem': 0,
                'num_cpu': 1,
                'cpu_time': 0}
        # TODO: mapping ec2 state to openstack state
        else:
            return {'state': power_state.RUNNING,
                'max_mem': 0,
                'mem': 0,
                'num_cpu': 1,
                'cpu_time': 0}

    def destroy(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None):
        """Destroy VM instance."""
        # TODO: handle destroy_disks flag later
        ec2_instance_id = self._get_ec2_instance_id(instance['uuid'])
        self.aws_ec2_java_server.deleteInstance(ec2_instance_id)

    def _get_ec2_instance_id(self, instance_uuid):
        """map openstack instance_uuid to ec2 instance id"""
        if instance_uuid not in self.instances.keys():
            ec2_instance_id = self.aws_ec2_java_server.getInstanceIdFromName(
                instance_uuid)
            self.instances[instance_uuid] = ec2_instance_id
        else:
            ec2_instance_id = self.instances[instance_uuid]
        return ec2_instance_id

    def get_volume_connector(self, instance):
        pass
