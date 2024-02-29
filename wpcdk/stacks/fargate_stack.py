from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_efs as efs,
)
from constructs import Construct
from .network_stack import NetworkStack
from .rds_stack import RdsStack
from .efs_stack import EfsStack

class FargateStack(Stack):
    def __init__(self, scope: Construct, id: str, network_stack: NetworkStack, rds_stack: RdsStack, efs_stack: EfsStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Reference to the RDS instance's secret
        db_credentials_secret = rds_stack.db_instance.secret

        # Reference to the EFS file system created in the EfsStack
        file_system = efs_stack.efs

        # Create an ECS cluster
        cluster = ecs.Cluster(self, "WordpressCluster", vpc=network_stack.vpc)

        # Define the task definition with WordPress container
        task_definition = ecs.FargateTaskDefinition(self, "WordpressTask")

        # Add WordPress container
        wordpress_container = task_definition.add_container("wordpress",
            image=ecs.ContainerImage.from_registry("bitnami/wordpress"),
            environment={
                # Database environment variables using secret values
                "WORDPRESS_DB_HOST": db_credentials_secret.secret_value_from_json("host").to_string(),
                "WORDPRESS_DB_USER": db_credentials_secret.secret_value_from_json("username").to_string(),
                "WORDPRESS_DB_PASSWORD": db_credentials_secret.secret_value_from_json("password").to_string(),
                "WORDPRESS_DB_NAME": "wordpress"
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="wordpress")
        )

        # Mount EFS to the WordPress container
        wordpress_container.add_mount_points(ecs.MountPoint(
            container_path="/bitnami/wordpress",
            source_volume="wordpress-data",
            read_only=False
        ))
        task_definition.add_volume(ecs.Volume(
            name="wordpress-data",
            efs_volume_configuration=ecs.EfsVolumeConfiguration(
                file_system_id=file_system.file_system_id
            )
        ))

        # Define the Fargate service
        service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "WordpressService",
            cluster=cluster,
            task_definition=task_definition,
            public_load_balancer=True
        )

        # Open port 80 on the container for web traffic
        wordpress_container.add_port_mappings(ecs.PortMapping(container_port=80, host_port=80))
