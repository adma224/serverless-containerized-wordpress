from aws_cdk import App
from stacks.network_stack import NetworkStack
from stacks.db_stack import AuroraServerlessStack
from stacks.efs_stack import EfsStack
from stacks.fargate_stack import FargateStack

app = App()

# Instantiate the NetworkStack
network_stack = NetworkStack(app, "NetworkStack")

# Instantiate other stacks, passing the network_stack as needed

db_stack = AuroraServerlessStack(app, "RdsStack", network_stack=network_stack)
efs_stack = EfsStack(app, "EfsStack", network_stack=network_stack)
fargate_stack = FargateStack(app, "AlbStack", network_stack=network_stack)

app.synth()
