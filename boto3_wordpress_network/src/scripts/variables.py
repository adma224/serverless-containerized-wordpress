# variables.py

# VPC Configuration
vpc_cidr_block = '10.0.0.0/16'

# Subnet Configuration
public_subnet_a_cidr = '10.0.1.0/24'
public_subnet_b_cidr = '10.0.2.0/24'
private_subnet_a_cidr = '10.0.3.0/24'
private_subnet_b_cidr = '10.0.4.0/24'

# Availability Zones
availability_zone_a = 'us-west-2a'
availability_zone_b = 'us-west-2b'

# Resource Names

## VPC
vpc_name = 'wordpress-serverless-vpc'

## Subnets
public_subnet_a_name = 'public-subnet-A'
public_subnet_b_name = 'public-subnet-B'
private_subnet_a_name = 'private-subnet-A'
private_subnet_b_name = 'private-subnet-B'

## Internet Gateway
igw_name = 'wordpress-serverless-igw'

## Elastic IP Names
eip_nat_gateway_a_name = 'wordpress-eip-nat-gateway-a'
eip_nat_gateway_b_name = 'wordpress-eip-nat-gateway-b'

## NAT GAteways
nat_gateway_a_name = 'wordpress-nat-gateway-a'
nat_gateway_b_name = 'wordpress-nat-gateway-b'

## Route Tables
public_route_table_name = 'wordpress-public-route-table'
private_route_table_a_name = 'wordpress-private-route-table-a'
private_route_table_b_name = 'wordpress-private-route-table-b'

## Security Groups
alb_security_group_name = 'ALB_group'
rds_security_group_name = 'RDS_group'
efs_security_group_name = 'EFS_group'
