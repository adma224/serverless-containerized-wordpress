#!/usr/bin/env python3

import aws_cdk as core
from stacks.network_stack import NetworkStack
from stacks.efs_stack import EfsStack
from stacks.rds_stack import RdsStack

app = core.App()

network_stack = NetworkStack(app, "NetworkStack", env={'region': 'us-east-1'})
#efs_stack = EfsStack(app, "EfsStack", vpc_stack=vpc_stack, env={'region': 'us-east-1'})
#rds_stack = RdsStack(app, "RdsStack", vpc_stack=vpc_stack, env={'region': 'us-east-1'})

app.synth()
