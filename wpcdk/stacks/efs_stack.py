from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_efs as efs,
    Duration
)
from constructs import Construct
from .network_stack import NetworkStack  # Adjust the import path as necessary

class EfsStack(Stack):
    def __init__(self, scope: Construct, id: str, network_stack: NetworkStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create a security group for EFS within the network stack's VPC
        efs_security_group = ec2.SecurityGroup(
            self, "EFSSecurityGroup",
            vpc=network_stack.vpc,
            description="Security Group for EFS",
        )
        
        # Allow NFS access from within the VPC
        efs_security_group.add_ingress_rule(
            ec2.Peer.ipv4(network_stack.vpc.vpc_cidr_block),
            ec2.Port.tcp(2049),
            "Allow NFS access from within the VPC"
        )

        # Define the EFS FileSystem
        self.efs_file_system = efs.FileSystem(
            self, "MyEFS",
            vpc=network_stack.vpc,
            security_group=efs_security_group,
            lifecycle_policy=efs.LifecyclePolicy.AFTER_7_DAYS,  # Automatically transition files to EFS Infrequent Access
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=efs.ThroughputMode.BURSTING,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Adjust based on your use case
            encrypted=True,
        )

        # Optionally, you can create an EFS access point here
        efs_access_point = self.efs_file_system.add_access_point("EFSAccessPoint",
            path="/export",
            posix_user=efs.PosixUser(uid="1001", gid="1001"),
            create_acl=efs.Acl(owner_uid="1001", owner_gid="1001", permissions="750"),
        )
