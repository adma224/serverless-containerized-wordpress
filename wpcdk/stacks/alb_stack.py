from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct
from .network_stack import NetworkStack  # Adjust the import path as necessary

class AlbStack(Stack):
    def __init__(self, scope: Construct, id: str, network_stack: NetworkStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create a security group for the ALB
        alb_security_group = ec2.SecurityGroup(
            self, "ALBSecurityGroup",
            vpc=network_stack.vpc,
            description="ALB Security Group",
        )
        
        # Allow inbound HTTP traffic on port 80
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow inbound HTTP access"
        )

        # Create the ALB
        self.alb = elbv2.ApplicationLoadBalancer(
            self, "WordPressALB",
            vpc=network_stack.vpc,
            internet_facing=True,
            security_group=alb_security_group,
            load_balancer_name="wof-load-balancer"
        )

        # Create a target group
        self.target_group = elbv2.ApplicationTargetGroup(
            self, "WordPressTargetGroup",
            vpc=network_stack.vpc,
            target_type=elbv2.TargetType.IP,
            port=8080,
            protocol=elbv2.ApplicationProtocol.HTTP,
            health_check={
                "port": "8080"
            },
            target_group_name="WordPressTargetGroup"
        )

        # Add a listener
        self.listener = self.alb.add_listener(
        "Listener",
        port=80,
        open=True  
        )
        self.listener.add_target_groups('Target', target_groups=[self.target_group])



