from aws_cdk import (
    Stack, aws_ec2 as ec2
)
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Correctly initialize the VPC with the 'cidr' argument
        self.vpc = ec2.Vpc(
            self, "vpc-wp-serverless",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),  # Corrected from 'vpc_cidr' to 'cidr'
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public-subnet", 
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private-subnet", 
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,  # Assuming this was already corrected
                    cidr_mask=24
                ),
            ],
            nat_gateways=2,
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )


        # Example: Add an Internet Gateway for public subnets
        self.internet_gateway = ec2.CfnInternetGateway(
            self, "igw-wp-serverless"
        )
        ec2.CfnVPCGatewayAttachment(
            self, "vpc-gateway-attachment",
            vpc_id=self.vpc.vpc_id,
            internet_gateway_id=self.internet_gateway.ref
        )

        # Example: Define public route table and associate with public subnets
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
        
        # Additional configurations can be placed here, such as VPC Endpoints, Flow Logs, etc.
