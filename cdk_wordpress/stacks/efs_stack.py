from aws_cdk import (
  Stack, 
  RemovalPolicy
)
import aws_cdk as cdk

from aws_cdk import (
  aws_ec2 as ec2,
  aws_efs as efs
)

from constructs import Construct
from .network_stack import NetworkStack  

class EfsStack(Stack):
    def __init__(self, scope: Construct, id: str, network_stack: NetworkStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        efs_security_group = ec2.SecurityGroup(
            self, "efs-group",
            vpc=network_stack.vpc,
            description="Security Group for EFS",
        )
        
        efs_security_group.add_ingress_rule(
            ec2.Peer.ipv4(network_stack.vpc.vpc_cidr_block),
            ec2.Port.tcp(2049),
            "Allow NFS access from within the VPC"
        )

        self.efs_file_system = efs.FileSystem(
            self, "efs-wp-serverless",
            vpc=network_stack.vpc,
            security_group=efs_security_group,
            lifecycle_policy=efs.LifecyclePolicy.AFTER_7_DAYS,  
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=efs.ThroughputMode.BURSTING,
            removal_policy=cdk.RemovalPolicy.DESTROY, 
            encrypted=True,
        )

        efs_access_point = self.efs_file_system.add_access_point("efs-access-point",
            path="/export",
            posix_user=efs.PosixUser(uid="1001", gid="1001"),
            create_acl=efs.Acl(owner_uid="1001", owner_gid="1001", permissions="750"),
        )
