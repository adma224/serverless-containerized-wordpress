
# Serverless WordPress Deployment with AWS CDK

Deploy a serverless WordPress site on AWS utilizing the AWS Cloud Development Kit (CDK). This setup includes a VPC, ECS Fargate, RDS Aurora Serverless, EFS for shared storage, and an Application Load Balancer.

## Prerequisites

Ensure you have the following installed:

- **AWS CLI**: [Install/update the AWS CLI](https://aws.amazon.com/cli/)
- **Node.js**: [Install Node.js](https://nodejs.org/) (including NPM)
- **AWS CDK**: After installing Node.js, install the AWS CDK by running `npm install -g aws-cdk`
- **Python**: [Install Python](https://www.python.org/downloads/)

## Setup

1. **Configure AWS CLI**

   Make sure you have configured the AWS CLI with your credentials and default region. You can do this by running:

   ```bash
   aws configure

Clone the Repository
Clone this repository to your local machine to get started.

git clone <repository-url>
cd wpcdk
Install Python Dependencies

Install the required Python dependencies listed in the requirements.txt file.

pip install -r requirements.txt
Bootstrap the AWS Environment for CDK

If this is your first time using CDK in this AWS account/region, you'll need to bootstrap your environment. Bootstrapping is a one-time operation for each AWS account and region.

cdk bootstrap
Deploy the CDK Stack

Deploy your stack to AWS. Ensure you are in the directory containing app.py before running the deployment command.

cdk deploy
This command deploys the entire infrastructure defined in your CDK app. Follow any prompts to approve the deployment.

Usage
After deployment, your WordPress site will be accessible through the URL of the Application Load Balancer created by the stack. You can find the ALB URL in the Outputs section of your CloudFormation stack in the AWS Management Console.

Clean Up
To avoid incurring future charges, remember to delete the resources when you're done.

cdk destroy
This command will remove the resources defined by the CDK from your AWS account.