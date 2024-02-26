import boto3
import variables as var

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')
rds_client = boto3.client('rds')
efs_client = boto3.client('efs')
elbv2_client = boto3.client('elbv2')

# Create VPC
vpc = ec2_resource.create_vpc(CidrBlock=var.vpc_cidr_block)
vpc.wait_until_available()
vpc.create_tags(Tags=[{'Key': 'Name', 'Value': var.vpc_name}])

# Create public subnets
public_subnet_a = vpc.create_subnet(CidrBlock=var.public_subnet_a_cidr, AvailabilityZone=var.availability_zone_a)
public_subnet_a.create_tags(Tags=[{'Key': 'Name', 'Value': var.public_subnet_a_name}])

public_subnet_b = vpc.create_subnet(CidrBlock=var.public_subnet_b_cidr, AvailabilityZone=var.availability_zone_b)
public_subnet_b.create_tags(Tags=[{'Key': 'Name', 'Value': var.public_subnet_b_name}])

# Create private subnets
private_subnet_a = vpc.create_subnet(CidrBlock=var.private_subnet_a_cidr, AvailabilityZone=var.availability_zone_a)
private_subnet_a.create_tags(Tags=[{'Key': 'Name', 'Value': var.private_subnet_a_name}])

private_subnet_b = vpc.create_subnet(CidrBlock=var.private_subnet_b_cidr, AvailabilityZone=var.availability_zone_b)
private_subnet_b.create_tags(Tags=[{'Key': 'Name', 'Value': var.private_subnet_b_name}])

# Create and attach Internet Gateway
igw = ec2_resource.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=igw.id)
igw.create_tags(Tags=[{'Key': 'Name', 'Value': var.igw_name}])

# Create route table for public subnets
public_route_table = vpc.create_route_table()
public_route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=igw.id)
public_route_table.associate_with_subnet(SubnetId=public_subnet_a.id)
public_route_table.associate_with_subnet(SubnetId=public_subnet_b.id)
public_route_table.create_tags(Tags=[{'Key': 'Name', 'Value': var.public_route_table_name}])

# Allocate Elastic IPs and create NAT Gateways
eip_a = ec2_client.allocate_address(Domain='vpc')
eip_b = ec2_client.allocate_address(Domain='vpc')

# Create NAT Gateway in the public subnet A and B
nat_gateway_a = ec2_client.create_nat_gateway(SubnetId=public_subnet_a.id, AllocationId=eip_a['AllocationId'])
nat_gateway_b = ec2_client.create_nat_gateway(SubnetId=public_subnet_b.id, AllocationId=eip_b['AllocationId'])

# Wait for NAT Gateways to be available
ec2_client.get_waiter('nat_gateway_available').wait(NatGatewayIds=[nat_gateway_a['NatGateway']['NatGatewayId']])
ec2_client.get_waiter('nat_gateway_available').wait(NatGatewayIds=[nat_gateway_b['NatGateway']['NatGatewayId']])

# Tag NAT Gateways
ec2_client.create_tags(Resources=[nat_gateway_a['NatGateway']['NatGatewayId']], Tags=[{'Key': 'Name', 'Value': var.nat_gateway_a_name}])
ec2_client.create_tags(Resources=[nat_gateway_b['NatGateway']['NatGatewayId']], Tags=[{'Key': 'Name', 'Value': var.nat_gateway_b_name}])

# Create Route Tables for Private Subnets and associate them
private_route_table_a = vpc.create_route_table()
private_route_table_a.create_route(DestinationCidrBlock='0.0.0.0/0', NatGatewayId=nat_gateway_a['NatGateway']['NatGatewayId'])
private_route_table_a.associate_with_subnet(SubnetId=private_subnet_a.id)
private_route_table_a.create_tags(Tags=[{'Key': 'Name', 'Value': var.private_route_table_a_name}])

private_route_table_b = vpc.create_route_table()
private_route_table_b.create_route(DestinationCidrBlock='0.0.0.0/0', NatGatewayId=nat_gateway_b['NatGateway']['NatGatewayId'])
private_route_table_b.associate_with_subnet(SubnetId=private_subnet_b.id)
private_route_table_b.create_tags(Tags=[{'Key': 'Name', 'Value': var.private_route_table_b_name}])

# Create ALB Security Group

alb_security_group = ec2_client.create_security_group(
    GroupName=var.alb_security_group_name,
    Description='Security Group for Application Load Balancer Allowing Web Traffic',
    VpcId=vpc.id  
)

ec2_client.authorize_security_group_ingress(
    GroupId=alb_security_group['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,
            'ToPort': 443,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)

# Create RDS Security Group
rds_security_group = ec2_client.create_security_group(
    GroupName=var.rds_security_group_name,
    Description='Security Group for RDS MySQL Access',
    VpcId=vpc.id
)

# Authorize MySQL traffic on port 3306 from within the VPC
ec2_client.authorize_security_group_ingress(
    GroupId=rds_security_group['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 3306,
            'ToPort': 3306,
            'IpRanges': [{'CidrIp': '10.0.0.0/16'}]  # Adjust the CIDR to match your VPC's CIDR block
        }
    ]
)

# Create EFS Security Group
efs_security_group = ec2_client.create_security_group(
    GroupName=var.efs_security_group_name,
    Description='Security Group for EFS Access',
    VpcId=vpc.id
)

# Authorize NFS traffic on port 2049 from within the VPC
ec2_client.authorize_security_group_ingress(
    GroupId=efs_security_group['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 2049,
            'ToPort': 2049,
            'IpRanges': [{'CidrIp': '10.0.0.0/16'}]  # Adjust the CIDR to match your VPC's CIDR block
        }
    ]
)
