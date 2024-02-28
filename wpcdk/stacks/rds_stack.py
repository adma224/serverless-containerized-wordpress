from aws_cdk import aws_rds as rds, core
from .vpc_stack import VpcStack

class RdsStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc_stack: VpcStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.db_instance = rds.DatabaseInstance(
            self, "MyDatabase",
            database_name="mydb",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_12_3),
            vpc=vpc_stack.vpc,
            vpc_subnets={
                "subnet_type": core.SubnetType.PRIVATE
            },
            allocated_storage=20,
            max_allocated_storage=100,
            instance_type=core.InstanceType.of(core.InstanceClass.BURSTABLE2, core.InstanceSize.MICRO),
            multi_az=False,
            auto_minor_version_upgrade=True,
            delete_automated_backups=True,
            backup_retention=core.Duration.days(7),
            publicly_accessible=False,
            security_groups=[],  # Define security groups or leave empty
        )
