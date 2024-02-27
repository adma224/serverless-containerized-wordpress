import boto3
import sys
import variables as v  # Ensure this module defines all required variables
from botocore.exceptions import ClientError

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

def get_or_create_vpc(name, cidr_block):
    try:
        vpcs = list(ec2_resource.vpcs.filter(Filters=[{'Name': 'tag:Name', 'Values': [name]}]))
        if vpcs:
            print(f"VPC '{name}' already exists with ID: {vpcs[0].id}")
            return vpcs[0]
        else:
            vpc = ec2_resource.create_vpc(CidrBlock=cidr_block)
            vpc.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
            vpc.wait_until_available()
            print(f"VPC '{name}' created with ID: {vpc.id}")
            return vpc
    except ClientError as e:
        print(f"Failed to get or create VPC: {e}")
        return None

def get_or_create_subnet(vpc, cidr_block, availability_zone, name):
    try:
        subnets = list(vpc.subnets.filter(Filters=[{'Name': 'tag:Name', 'Values': [name]}, {'Name': 'availability-zone', 'Values': [availability_zone]}]))
        if subnets:
            print(f"Subnet '{name}' already exists in {availability_zone} with ID: {subnets[0].id}")
            return subnets[0]
        else:
            subnet = vpc.create_subnet(CidrBlock=cidr_block, AvailabilityZone=availability_zone)
            subnet.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
            print(f"Subnet '{name}' created in {availability_zone} with ID: {subnet.id}")
            return subnet
    except ClientError as e:
        print(f"Failed to get or create Subnet: {e}")
        return None

def get_or_create_internet_gateway(vpc, name):
    try:
        # Check for existing Internet Gateways with the specified name tag
        igws = list(ec2_resource.internet_gateways.filter(Filters=[{'Name': 'tag:Name', 'Values': [name]}]))
        if igws:
            print(f"Internet Gateway '{name}' already exists with ID: {igws[0].id}")
            return igws[0]
        else:
            # If no existing IGW is found, create a new one and attach it to the VPC
            igw = ec2_resource.create_internet_gateway()
            igw.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
            vpc.attach_internet_gateway(InternetGatewayId=igw.id)
            print(f"Internet Gateway '{name}' created and attached to VPC {vpc.id} with ID: {igw.id}")
            return igw
    except ClientError as e:
        print(f"Failed to get or create Internet Gateway: {e}")
        return None

def get_or_allocate_eip(name):
    try:
        # Checking if an Elastic IP with the given name tag exists
        eips = ec2_client.describe_addresses(Filters=[{'Name': 'tag:Name', 'Values': [name]}])
        if eips['Addresses']:
            eip = eips['Addresses'][0]
            print(f"Elastic IP '{name}' already exists with Allocation ID: {eip['AllocationId']}")
            return eip
        else:
            allocation = ec2_client.allocate_address(Domain='vpc')
            ec2_client.create_tags(Resources=[allocation['AllocationId']], Tags=[{'Key': 'Name', 'Value': name}])
            print(f"Elastic IP '{name}' allocated with Allocation ID: {allocation['AllocationId']}")
            return allocation
    except ClientError as e:
        print(f"Failed to get or allocate Elastic IP: {e}")
        return None

def create_nat_gateway(subnet, allocation_id, name):
    try:
        nat_gateway_response = ec2_client.create_nat_gateway(SubnetId=subnet.id, AllocationId=allocation_id)
        nat_gateway_id = nat_gateway_response['NatGateway']['NatGatewayId']
        print(f"NAT Gateway '{name}' creation initiated with ID: {nat_gateway_id}")

        # Waiting for NAT Gateway to become available
        ec2_client.get_waiter('nat_gateway_available').wait(NatGatewayIds=[nat_gateway_id])
        print(f"NAT Gateway '{name}' is now available.")

        ec2_client.create_tags(Resources=[nat_gateway_id], Tags=[{'Key': 'Name', 'Value': name}])
        return nat_gateway_id
    except ClientError as e:
        print(f"Failed to get or create NAT Gateway: {e}")
        return None

def add_route_to_nat(route_table, nat_gateway_id):
    try:
        # Attempt to create a route in the specified route table directed to the NAT Gateway
        route = route_table.create_route(
            DestinationCidrBlock='0.0.0.0/0',  # Typically, for Internet access
            NatGatewayId=nat_gateway_id
        )
        print(f"Route to NAT Gateway {nat_gateway_id} added to Route Table {route_table.id}")
    except ClientError as e:
        print(f"Failed to add route to NAT Gateway: {e}")


def get_or_create_route_table(vpc, name):
    try:
        route_tables = list(vpc.route_tables.filter(Filters=[{'Name': 'tag:Name', 'Values': [name]}]))
        if route_tables:
            print(f"Route table '{name}' already exists with ID: {route_tables[0].id}")
            return route_tables[0]
        else:
            route_table = vpc.create_route_table()
            route_table.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
            print(f"Route table '{name}' created with ID: {route_table.id}")
            return route_table
    except ClientError as e:
        print(f"Failed to get or create Route Table: {e}")
        return None

def associate_subnet_with_route_table(subnet_id, route_table_id):
    try:
        route_table = ec2_resource.RouteTable(route_table_id)
        # Check if the subnet is already associated
        for association in route_table.associations_all():
            if association.subnet_id == subnet_id:
                print(f"Subnet {subnet_id} is already associated with Route Table {route_table_id}.")
                return association.id

        # If the subnet is not already associated, create a new association
        association = route_table.associate_with_subnet(SubnetId=subnet_id)
        print(f"Successfully associated Subnet {subnet_id} with Route Table {route_table_id}. Association ID: {association.id}")
        return association.id
    except Exception as e:
        print(f"Error associating Subnet {subnet_id} with Route Table {route_table_id}: {e}")
        return None

def main():
    # VPC
    vpc = get_or_create_vpc(v.vpc_name, v.vpc_cidr_block)
    
    # Subnets
    public_subnet_a = get_or_create_subnet(vpc, v.public_subnet_a_cidr, v.availability_zone_a, v.public_subnet_a_name)
    public_subnet_b = get_or_create_subnet(vpc, v.public_subnet_b_cidr, v.availability_zone_b, v.public_subnet_b_name)
    private_subnet_a = get_or_create_subnet(vpc, v.private_subnet_a_cidr, v.availability_zone_a, v.private_subnet_a_name)
    private_subnet_b = get_or_create_subnet(vpc, v.private_subnet_b_cidr, v.availability_zone_b, v.private_subnet_b_name)
    
    # Internet Gateway
    igw = get_or_create_internet_gateway(vpc, v.igw_name)
    
    # Route Tables and Associations
    public_route_table = get_or_create_route_table(vpc, v.public_route_table_name)
    associate_subnet_with_route_table(public_subnet_a, public_route_table)
    associate_subnet_with_route_table(public_subnet_b, public_route_table)
    
    # Elastic IPs for NAT Gateways
    eip_nat_gateway_a = get_or_allocate_eip(v.eip_nat_gateway_a_name)
    eip_nat_gateway_b = get_or_allocate_eip(v.eip_nat_gateway_b_name)
    
    # NAT Gateways
    nat_gateway_a = create_nat_gateway(public_subnet_a, eip_nat_gateway_a['AllocationId'], v.nat_gateway_a_name)
    nat_gateway_b = create_nat_gateway(public_subnet_b, eip_nat_gateway_b['AllocationId'], v.nat_gateway_b_name)
    
    # Private Route Tables and Associations for NAT
    private_route_table_a = get_or_create_route_table(vpc, v.private_route_table_a_name)
    private_route_table_b = get_or_create_route_table(vpc, v.private_route_table_b_name)
    associate_subnet_with_route_table(private_subnet_a.id, private_route_table_a)
    associate_subnet_with_route_table(private_subnet_b.id, private_route_table_b)
    
    # Add routes for NAT Gateways in private route tables
    add_route_to_nat(private_route_table_a, nat_gateway_a['NatGatewayId'])
    add_route_to_nat(private_route_table_b, nat_gateway_b['NatGatewayId'])

    alb_security_group = ec2_client.create_security_group(
        GroupName=v.alb_security_group_name,
        Description='Security Group for Application Load Balancer Allowing Web Traffic',
        VpcId=vpc.id  
    )
    try:
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
    except ClientError as e:
        print(f"Failed to get or create Route Table: {e}")
        return None
    
    try:

        # Create RDS Security Group
        rds_security_group = ec2_client.create_security_group(
            GroupName=v.rds_security_group_name,
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
                    'IpRanges': [{'CidrIp': v.vpc_cidr_block}]  # Adjust the CIDR to match your VPC's CIDR block
                }
            ]
        )
    except ClientError as e:
        print(f"Failed to get or create Route Table: {e}")
        return None

    try:
        # Create EFS Security Group
        efs_security_group = ec2_client.create_security_group(
            GroupName=v.efs_security_group_name,
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
                    'IpRanges': [{'CidrIp': v.vpc_cidr_block}]  # Adjust the CIDR to match your VPC's CIDR block
                }
            ]
        )
    except ClientError as e:
        print(f"Failed to get or create Route Table: {e}")
        return None

if __name__ == "__main__":
    main()
