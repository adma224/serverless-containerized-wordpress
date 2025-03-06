from aws_cdk import (
    Stack, aws_ec2 as ec2
)
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        
        # Creatng VPC:
        #   Availability Zones = 2
        #   CIDR Block = 10.0.0.0/16
        #   Subnets per AZ = public-subnet, private-subnet
        #   NAT Gatweay = 2
        #   Network Load Balancer = 1 (Created Implicitly with the Creation of VPC across 2 AZs)
        #   Internet Gateway = 1 (Connected to Load Balancer)

        self.vpc = ec2.Vpc(
            self, "vpc-wp-serverless",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"), 
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public-subnet", 
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private-subnet", 
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS, 
                    cidr_mask=24
                ),
            ],
            nat_gateways=2,
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )
        self.internet_gateway = ec2.CfnInternetGateway(
            self, "igw-wp-serverless"
        )
        ec2.CfnVPCGatewayAttachment(
            self, "vpc-gateway-attachment",
            vpc_id=self.vpc.vpc_id,
            internet_gateway_id=self.internet_gateway.ref
        )

        self.public_route_table = ec2.CfnRouteTable(
            self, "public-routetable",
            vpc_id=self.vpc.vpc_id
        )
        for subnet in self.vpc.public_subnets:
            ec2.CfnSubnetRouteTableAssociation(
                self, f"routetable-association-{subnet.node.id}",
                subnet_id=subnet.subnet_id,
                route_table_id=self.public_route_table.ref
            )
        ec2.CfnRoute(
            self, "public-route",
            route_table_id=self.public_route_table.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=self.internet_gateway.ref
        )
        
