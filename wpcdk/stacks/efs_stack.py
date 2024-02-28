from aws_cdk import aws_efs as efs, core
from .vpc_stack import VpcStack

class EfsStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc_stack: VpcStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.efs = efs.FileSystem(
            self, "MyEfs",
            vpc=vpc_stack.vpc,
            lifecycle_policy=efs.LifecyclePolicy.AFTER_7_DAYS,  # Deletes files after 7 days of not being accessed
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=efs.ThroughputMode.BURSTING
        )
