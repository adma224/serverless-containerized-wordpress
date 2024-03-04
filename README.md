# Serverless Containerized WordPress Site with Infrastructure as Code (IaC) via CloudFormation



[Infrastructure Diagram](https://github.com/adma224/serverless-containerized-wordpress/blob/main/infrastructure_diagram.png)

[Design Narrative + Video](http://54.148.225.217/) (Under Construction)

This project uses **WordPress** container images and leverages AWS Fargate as the serverless orchestration engine. This project idea and some of its architecture is based on Parmar and Hayes's [Running WordPress on Amazon ECS and AWS Fargate with Amazon EFS](https://aws.amazon.com/blogs/containers/running-wordpress-amazon-ecs-fargate-ecs/) with the following adjustments for scalability, interpretability, and achieving a fully serverless architecture:

- **Amazon Cloud Development Kit (CDK)** is used for developing a CloudFormation template with Python code. This allows for deploying our entire application using Infrastructure as Code principles, instead of using a combination of CLI Console Commands and a CloudFormation Template as the article suggests. Using the CDK allows us to develop a much richer and complete CloudFormation Template but also allows us to go back to our code and change our "Stacks" whenever we want to make changes to the architecture, rather than editing the CloudFormation Template directly.
- **AWS Secrets Manager** allows us to create and manage secrets. For this project, I wanted to fix certain security issues from the source project. Namely, this prevents hard-coding specific user names and passwords into our CloudFormation template (for the SQL databes) and to change the default username and password of the WordPress container images before deployment. From the AWS Secrets Manager console, we can easily view, manage, and retrieve our stored secrets, provided we have the appropriate IAM permissions.
- Using **Amazon Aurora Serverless** rather than AWS RDS allows us to deploy a SQL database that requires no management of resources and frees us from having to worry about scalability and availability of our SQL databases. Aurora automatically provisions resources and you only pay for I/O operations and storage, rather than the underlying computing resources mantaining a SQL database. For such a small deployment it is objectively simpler and more cost effective to use Aurora Serverless.

That being said, the original article serves as a useful template for building our architecture on top of. The following aspects are based on the source article
- VPC and Network configurations (with small adjustments to adapt to CDK's creation methods)
- Application Load Balancer
- AWS Elastic File Server (EFS) for parallel file system deployment

The architecture ensures high availability by deploying resources across multiple availability zones and automates resource provisioning using Boto3, the AWS SDK for Python.

## Boto3 vs CDK

You may have noticed that there are two folders in this directory:

- cdk_wordpress_cloudformation
- boto3_wordpress_network

When setting up this serverless WordPress project, I faced a choice: script everything with Boto3 for absolute control or use the AWS Cloud Development Kit (CDK) for its convenience and power. Here's why CDK became my go-to:

- **Efficiency:** CDK streamlines the deployment process. Writing in familiar programming languages and leveraging the constructs library saved me countless hours.

- **Maintainability:** With CDK, infrastructure changes are a commit away. It's easier to iterate and maintain than sifting through JSON or YAML templates or scripting detailed steps in Boto3.

- **Abstraction:** CDK abstracts away the complexity without sacrificing control. It allows for defining high-level components that Boto3 handles manually, making my infrastructure code cleaner and more readable.

That being said, I prefer to name every single one of my resources depending on the specific project and role they have within my application. Using Boto3 for the vpc configuration step is a preferred option since you manually create an provision AWS networking resources infividually, giving you the opportunity of providing them a name or other aws resource tags. Also, it allows you to explicilty create Networking resources for better control of what is beiung created. The CDK automatically provisions resources such as Application Load Balancers, NAT Gateways, and Internet Gateways with the creation of different aws resources (ECS Clusters, Private Subnet, and Public Subnet respectively). Also, the CDK does not allow an easy way to name each resource separately. For this reason I have included a separate folder for using Boto3 to provision networking resources.

The README.md files of each of these folders has more in-depth information about the file structure, the breakdown of each file and its contents, and instructions on how to run them.

## Overview of Resources

### Network

**Amazon VPC (Virtual Private Cloud)** - Explicitly defined in my NetworkStack. This acts as the networking foundation, providing an isolated section of the AWS Cloud where I can launch AWS resources in a defined virtual network.

**Application Load Balancer (ALB)** - Implicitly created by FargateStack through ECS patterns. The ALB automatically distributes incoming application traffic across multiple targets, such as ECS tasks, in multiple Availability Zones, increasing the fault tolerance of my application.

**Security Groups** - I define several throughout the stacks for different purposes, such as controlling access to the RDS database, EFS, and the application itself. They act as a virtual firewall for the associated resources.

### SQL Database

**Amazon RDS Aurora Serverless** - Defined in AuroraServerlessStack, it provides a scalable and serverless relational database which automatically starts up, shuts down, and scales with the application's needs.

### File System



**Amazon EFS (Elastic File System)** - Set up in EfsStack, it offers a simple, scalable, elastic file storage for use with AWS Cloud services and on-premises resources. It's particularly useful for storing the WordPress content that needs to be shared across multiple instances.

**Amazon EFS Access Points** - Created within EfsStack to simplify file system access. This ensures my application has the appropriate file permissions and directory for the WordPress content.

### Containers

**Amazon ECS Service** - Implicitly created within FargateStack, it maintains the desired count of instances of the task definition. It integrates with the ALB for high availability and fault tolerance.

**Amazon ECS Fargate** - Managed by FargateStack, it allows me to run containers without managing servers or clusters. I use Fargate to deploy the WordPress application in a serverless fashion.

**Amazon ECS Task Definition** - Also managed by FargateStack. It's a blueprint for my application that describes the container and volume configuration.

**ECS Cluster** - Although implicitly created in the FargateStack, it's crucial as it provides the networking and orchestration framework for my containerized application.

### Other

**AWS Secrets Manager** - Utilized in AuroraServerlessStack for securely storing and managing database credentials. This allows my application to access the database without hardcoding sensitive information.




