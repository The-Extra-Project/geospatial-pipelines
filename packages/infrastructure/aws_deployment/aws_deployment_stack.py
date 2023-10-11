from aws_cdk import (
    Stack,
    aws_ecr as ECR,
    aws_ecs as ECS,
    aws_iam as IAM,
    aws_logs as logs,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_apigatewayv2 as api_gw,
    aws_secretsmanager as  secrets,
    
    # aws_ecs_patterns as ecs_patterns,
    # Names
)
import json
from pathlib import Path
import os
from constructs import Construct

class AwsDeploymentStack(Stack):
    container_service: ECR
    cluster: ECS
    vpc: ec2.Vpc
    pipeline_execution_role: IAM.Role
    bacalhau_api: api_gw.CfnApi
    lb_securityGroup: ec2.SecurityGroup
    
    subnetIds: list[any]
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ## now you can use the following possiblities 
        ## 1. defining a new VPC by yourselves (ec2.Vpc)
        ##2. or deploying from the existing VPC's using ec2.Vpc.from_lookup()
        ## 3. adding the neuralangelo_modified conntainer in the ECR and creating task for running the training jobs
               
        self.vpc = ec2.Vpc(self, "image-reconstruction-vpc", max_azs=1)

        
        print(function.connections)
    