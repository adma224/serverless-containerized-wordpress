from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    Stack,
)
from constructs import Construct
from .network_stack import NetworkStack

class AuroraServerlessStack(Stack):
    def __init__(self, scope: Construct, id: str, network_stack: NetworkStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define the username for the database
        username = 'admin'

        # Create a secret in AWS Secrets Manager for the RDS credentials
        db_credentials_secret = secretsmanager.Secret(
            self, "db-credentials",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "%s"}' % username,
                generate_string_key="password",
                exclude_characters='"@/\\',
            )
        )

        # Create a security group for the Aurora Serverless DB Cluster within the VPC
        db_security_group = ec2.SecurityGroup(
            self, "db-group",
            vpc=network_stack.vpc,
            description="Security Group for Aurora Serverless DB Cluster",
        )
        db_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(3306),
            "Allow MySQL access"
        )

        # Define the Aurora Serverless DB Cluster
        self.db_cluster = rds.ServerlessCluster(
            self, "wp-serverless-cluster",
            engine=rds.DatabaseClusterEngine.aurora_mysql(
                version=rds.AuroraMysqlEngineVersion.VER_2_08_1
            ),
            vpc=network_stack.vpc,
            credentials=rds.Credentials.from_secret(db_credentials_secret),  # Use credentials from Secrets Manager
            security_groups=[db_security_group],
            default_database_name="wp-db",
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
        )
