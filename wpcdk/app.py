from aws_cdk import App
from stacks.network_stack import NetworkStack
from stacks.alb_stack import AlbStack
from stacks.rds_stack import RdsStack
from stacks.efs_stack import EfsStack

app = App()

# Instantiate the NetworkStack
network_stack = NetworkStack(app, "NetworkStack")

# Instantiate other stacks, passing the network_stack as needed
#alb_stack = AlbStack(app, "AlbStack", network_stack=network_stack)
rds_stack = RdsStack(app, "RdsStack", network_stack=network_stack)
#efs_stack = EfsStack(app, "EfsStack", network_stack=network_stack)

app.synth()
