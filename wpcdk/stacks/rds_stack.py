from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    Duration
)
from constructs import Construct
from .network_stack import NetworkStack  # Adjust the import path as necessary

class RdsStack(Stack):
    def __init__(self, scope: Construct, id: str, network_stack: NetworkStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create a security group for RDS within the VPC provided by network_stack
        rds_security_group = ec2.SecurityGroup(
            self, "RDSSecurityGroup",
            vpc=network_stack.vpc,
            description="Security Group for RDS instance",
        )
        # Allow inbound MySQL/MariaDB access (default port 3306)
        rds_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(3306),
            "Allow MySQL/MariaDB access"
        )

        # Define the RDS instance
        self.db_instance = rds.DatabaseInstance(
            self, "MyRDSInstance",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_19
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            vpc=network_stack.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            ),
            security_groups=[rds_security_group],
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            backup_retention=Duration.days(7),
            deletion_protection=False,
            database_name="mydatabase",
            publicly_accessible=False,
            auto_minor_version_upgrade=True,
        )
