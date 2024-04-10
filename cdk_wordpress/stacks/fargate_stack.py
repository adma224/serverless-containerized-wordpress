from aws_cdk import (
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_efs as efs,
    aws_secretsmanager as secretsmanager,
    Stack,
)
from constructs import Construct
from .network_stack import NetworkStack
from .db_stack import AuroraServerlessStack
from .efs_stack import EfsStack

class FargateStack(Stack):
    def __init__(self, scope: Construct, id: str, network_stack: NetworkStack, rds_stack: RdsStack, efs_stack: EfsStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        db_credentials_secret = rds_stack.db_credentials_secret

        file_system = efs_stack.efs

        cluster = ecs.Cluster(self, "WordpressCluster", vpc=network_stack.vpc)

        task_definition = ecs.FargateTaskDefinition(self, "WordpressTask")

        wordpress_container = task_definition.add_container(
            "wordpress",
            image=ecs.ContainerImage.from_registry("bitnami/wordpress"),
            secrets={
                "WORDPRESS_DB_HOST": ecs.Secret.from_secrets_manager(db_credentials_secret, "host"),
                "WORDPRESS_DB_USER": ecs.Secret.from_secrets_manager(db_credentials_secret, "username"),
                "WORDPRESS_DB_PASSWORD": ecs.Secret.from_secrets_manager(db_credentials_secret, "password"),
                "WORDPRESS_USERNAME": ecs.Secret.from_secrets_manager(db_credentials_secret, "adminUsername"),
                "WORDPRESS_PASSWORD": ecs.Secret.from_secrets_manager(db_credentials_secret, "adminPassword"),
                "WORDPRESS_EMAIL": ecs.Secret.from_secrets_manager(db_credentials_secret, "adminEmail"),
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="wordpress"),
        )

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

        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "WordpressService",
            cluster=cluster,
            task_definition=task_definition,
            public_load_balancer=True,
        )

        wordpress_container.add_port_mappings(ecs.PortMapping(container_port=80, host_port=80))


        fargate_service.load_balancer.add_listener(
            "HTTPListener",
            port=80,
            open=True,
        )

        wordpress_container.add_port_mappings(ecs.PortMapping(container_port=80, host_port=80))
