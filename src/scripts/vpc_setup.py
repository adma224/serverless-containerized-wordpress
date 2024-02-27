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
public_subnet_a = vpc.create_subnet(CidrBlock=var.public_subnet_a_cidr, AvailabilityZone=var.availability_zone_a, MapPublicIpOnLaunch=True)
public_subnet_a.create_tags(Tags=[{'Key': 'Name', 'Value': var.public_subnet_a_name}])

public_subnet_b = vpc.create_subnet(CidrBlock=var.public_subnet_b_cidr, AvailabilityZone=var.availability_zone_b, MapPublicIpOnLaunch=True)
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





"""

EFS Creation Process

"""

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
            'IpRanges': [{'CidrIp': var.vpc_cidr_block}]  # Adjust the CIDR to match your VPC's CIDR block
        }
    ]
)

# Create an EFS file system with encryption enabled
efs_response = efs_client.create_file_system(
    Encrypted=True,
    PerformanceMode='generalPurpose',
    ThroughputMode='bursting',
    Tags=[{'Key': 'Name', 'Value': 'Wordpress-demo'}]
)
file_system_id = efs_response['FileSystemId']

private_subnet_ids = [private_subnet_a.id, private_subnet_b.id]

# Create mount targets for the EFS file system in the specified subnets
for subnet_id in private_subnet_ids:
    efs_client.create_mount_target(
        FileSystemId=file_system_id,
        SubnetId=subnet_id,
        SecurityGroups=[efs_security_group['GroupId']]
    )

# Create an access point
access_point = efs_client.create_access_point(
    FileSystemId=file_system_id,
    PosixUser={
        'Uid': '1000',
        'Gid': '1000'
    },
    RootDirectory={
        'Path': '/bitnami',
        'CreationInfo': {
            'OwnerUid': '1000',
            'OwnerGid': '1000',
            'Permissions': '0777'
        }
    }
)







# Create a Network ACL for the public subnet
public_nacl = ec2_client.create_network_acl(VpcId=vpc.id)
ec2_client.create_network_acl_entry(
    NetworkAclId=public_nacl['NetworkAcl']['NetworkAclId'],
    RuleNumber=100,
    Protocol="-1",
    RuleAction="allow",
    Egress=False,
    CidrBlock="0.0.0.0/0",
    PortRange={'From': 0, 'To': 65535},
)
ec2_client.create_network_acl_entry(
    NetworkAclId=public_nacl['NetworkAcl']['NetworkAclId'],
    RuleNumber=100,
    Protocol="-1",
    RuleAction="allow",
    Egress=True,
    CidrBlock="0.0.0.0/0",
    PortRange={'From': 0, 'To': 65535},
)

# Associate the Network ACL with the public subnet
ec2_client.associate_network_acl(NetworkAclId=public_nacl['NetworkAcl']['NetworkAclId'], SubnetId=public_subnet_a.id)
ec2_client.associate_network_acl(NetworkAclId=public_nacl['NetworkAcl']['NetworkAclId'], SubnetId=public_subnet_b.id)

# Repeat for private subnets if needed
# Create a Network ACL for the private subnet
private_nacl = ec2_client.create_network_acl(VpcId=vpc.id)
ec2_client.create_tags(Resources=[private_nacl['NetworkAcl']['NetworkAclId']], Tags=[{'Key': 'Name', 'Value': 'PrivateSubnetNACL'}])

# Add ingress rule to allow all traffic
ec2_client.create_network_acl_entry(
    NetworkAclId=private_nacl['NetworkAcl']['NetworkAclId'],
    RuleNumber=100,
    Protocol="-1",  # -1 means all protocols
    RuleAction="allow",
    Egress=False,  # False indicates ingress
    CidrBlock="0.0.0.0/0",
    PortRange={'From': 0, 'To': 65535}
)

# Add egress rule to allow all traffic
ec2_client.create_network_acl_entry(
    NetworkAclId=private_nacl['NetworkAcl']['NetworkAclId'],
    RuleNumber=100,
    Protocol="-1",  # -1 means all protocols
    RuleAction="allow",
    Egress=True,  # True indicates egress
    CidrBlock="0.0.0.0/0",
    PortRange={'From': 0, 'To': 65535}
)

# Associate the Network ACL with the private subnets
ec2_client.associate_network_acl(NetworkAclId=private_nacl['NetworkAcl']['NetworkAclId'], SubnetId=private_subnet_a.id)
ec2_client.associate_network_acl(NetworkAclId=private_nacl['NetworkAcl']['NetworkAclId'], SubnetId=private_subnet_b.id)


# Create an RDS MySQL instance (simplified example)
rds_instance = rds_client.create_db_instance(
    DBName=var.db_name,
    DBInstanceIdentifier=var.db_instance_identifier,
    AllocatedStorage=20,
    DBInstanceClass=var.db_instance_class,
    Engine='mysql',
    MasterUsername=var.db_master_username,
    MasterUserPassword=var.db_master_password,
    VpcSecurityGroupIds=[rds_security_group['GroupId']],
    Tags=[{'Key': 'Name', 'Value': 'MyRDSInstance'}]
)



# Create an ALB
alb_response = elbv2_client.create_load_balancer(
    Name=var.alb_name,
    Subnets=[public_subnet_a.id, public_subnet_b.id],
    SecurityGroups=[alb_security_group['GroupId']],
    Scheme='internet-facing',
    Tags=[{'Key': 'Name', 'Value': var.alb_name}],
    Type='application'
)

# Create a target group
target_group = elbv2_client.create_target_group(
    Name=var.target_group_name,
    Protocol='HTTP',
    Port=80,
    VpcId=vpc.id,
    HealthCheckProtocol='HTTP',
    HealthCheckPath='/',
    TargetType='instance'
)

# Create a listener
listener = elbv2_client.create_listener(
    LoadBalancerArn=alb_response['LoadBalancers'][0]['LoadBalancerArn'],
    Protocol='HTTP',
    Port=80,
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn': target_group['TargetGroups'][0]['TargetGroupArn']
        }
    ]
)

