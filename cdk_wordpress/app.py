from aws_cdk import App
from stacks.network_stack import NetworkStack
from stacks.db_stack import AuroraServerlessStack
from stacks.efs_stack import EfsStack
from stacks.fargate_stack import FargateStack

app = App()


"""

The following stacks will be created and deployed

- Network Stack: deploys 2 private subnets, 2 public subnets, and two AZs. Creates an ALB and an Iternet Gateway

- Database Stack: creates an Aurora Serverless SQL Database and saves the credentials of the DB to Secrets Manager

- EFS Stack: creates an elastic file system

- Fargate Stack: creates a Fargate service, saves the wordpress container image to ECR, and configures the wordpress container to reference the Aurora DB and EFS

"""

network_stack = NetworkStack(app, "NetworkStack")


db_stack = AuroraServerlessStack(app, "RdsStack", network_stack=network_stack)
efs_stack = EfsStack(app, "EfsStack", network_stack=network_stack)
fargate_stack = FargateStack(app, "AlbStack", network_stack=network_stack)

app.synth()
