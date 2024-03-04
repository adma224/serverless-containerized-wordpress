from aws_cdk import (
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    Stack,
)
from constructs import Construct
from .network_stack import NetworkStack
from .rds_stack import RdsStack
from .efs_stack import EfsStack

class FargateStack(Stack):
    def __init__(self, scope: Construct, id: str, network_stack: NetworkStack, rds_stack: RdsStack, efs_stack: EfsStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define the task definition with WordPress container
        task_definition = ecs.FargateTaskDefinition(self, "WordpressTask")

        # Add WordPress container
        wordpress_container = task_definition.add_container(
            "wordpress",
            image=ecs.ContainerImage.from_registry("bitnami/wordpress"),
            environment={
                # Database configuration
                "WORDPRESS_DB_HOST": rds_stack.db_instance.db_instance_endpoint_address,
                "WORDPRESS_DB_NAME": "wordpress",
                "WORDPRESS_DB_USER": "admin",  # Use the actual username
                "WORDPRESS_DB_PASSWORD": "your_secure_password",  # Use a secure password
                # Admin account configuration
                "WORDPRESS_USERNAME": "newadminusername",  # New admin username
                "WORDPRESS_PASSWORD": "newsecurepassword",  # New secure password
                "WORDPRESS_EMAIL": "admin@example.com",  # Admin email
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="wordpress"),
        )

        # Mount EFS to the WordPress container
        wordpress_container.add_mount_points(ecs.MountPoint(
            container_path="/bitnami/wordpress",
            source_volume="wordpress-data",
            read_only=False,
        ))
        task_definition.add_volume(ecs.Volume(
            name="wordpress-data",
            efs_volume_configuration=ecs.EfsVolumeConfiguration(
                file_system_id=file_system.file_system_id,
            ),
        ))

        # Define the Fargate service with an ALB
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "WordpressService",
            cluster=cluster,
            task_definition=task_definition,
            public_load_balancer=True,  # Set to `False` if the load balancer should be internal
            # Assign other properties as needed
        )

        # Add an additional listener on port 80 if needed
        fargate_service.load_balancer.add_listener(
            "HTTPListener",
            port=80,
            open=True,
        )

        # Open port 80 on the container for web traffic (if not already specified)
        wordpress_container.add_port_mappings(ecs.PortMapping(container_port=80, host_port=80))
