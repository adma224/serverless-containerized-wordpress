# WordPress on AWS ECS with Fargate
This project sets up a WordPress website using Amazon Elastic Container Service (ECS) with AWS Fargate and Amazon Elastic File System (EFS). It demonstrates how to deploy a scalable and serverless WordPress application within AWS, leveraging the power of containers and managed services for ease of use, scalability, and reliability.

## Overview
The setup includes creating a VPC, subnets, an Internet Gateway, Route Tables, NAT Gateways, and Security Groups to support a secure, scalable WordPress application on ECS using Fargate. The architecture ensures high availability by deploying resources across multiple availability zones and automates resource provisioning using Boto3, the AWS SDK for Python.

## Reference
This project is inspired by and adapted from the AWS blog post: "Running WordPress on Amazon ECS and AWS Fargate with Amazon EFS". The article provides insights into deploying WordPress on ECS with Fargate, highlighting the benefits of containerizing WordPress and using AWS managed services for scalability and manageability.

## Prerequisites
AWS Account
AWS CLI configured
Python and Boto3 installed
Basic knowledge of AWS services (ECS, Fargate, EFS, RDS)
