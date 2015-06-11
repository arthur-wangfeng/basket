"""
:mod:`ec2` -- Nova support for AWS EC2 through EC2 API.
"""
# NOTE(sdague) for nicer compute_driver specification
from nova.virt.ec2 import driver

AwsEc2Driver = driver.AwsEc2Driver