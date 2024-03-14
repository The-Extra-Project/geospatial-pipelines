from aws_cdk import (
    Stack,
    aws_ecr as ECR,
    aws_ecs as ECS,
    aws_iam as IAM,
    aws_logs as logs,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_apigatewayv2 as api_gw
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
               
        self.vpc = ec2.Vpc(self, "construction-pipeline-vpc", max_azs=1)

        ## creating vpc private link:
        
        self.lb_securityGroup = ec2.SubnetSelection(availability_zones=["us-east-1"])
        
        ## for now i have allowed all the outbound traffic in order to avoid the blocking of the bacalhau connections with the EC2.
        self.load_balancer_securityGroup = ec2.SecurityGroup(self,id="LB_pipeline_vpc", vpc=self.vpc, description="LB rules for only accessing the API_GW", allow_all_outbound=True)

        ## currently simplified for testing, but eventually be restricted to 1234 and 8080 (ports defined for the connection with the bacalhau)
        self.load_balancer_securityGroup.add_ingress_rule(
            connection=ec2.Port.all_tcp(),
            peer=ec2.Peer.any_ipv4(),
            description='Allow from anyone on port'
        )
        ## attaching the ECS layer for the corresponding VPC: 
        self.cluster = ECS.Cluster(self, "extralabs-dev-0.1", cluster_name="pointcoud", vpc=self.vpc)

        ## role for running the tasks on the ECS cluster (assigned to the API_GW etc).
        self.pipeline_execution_role = IAM.Role(self, "pipeline-pointcloud-execution-role", assumed_by=IAM.ServicePrincipal("ecs-tasks.amazonaws.com"),role_name="pipeline-running-agent")
        
        ## adding the description of policy regarding what the given role holder can access.
        ## NOTE: here the resources is defined as all of them which are defined based on your role, which at times can be too much permissive. so try to add only the given ARN's
        access_policy_statement = IAM.PolicyStatement(
            effect=IAM.Effect.ALLOW,
            resources=[
                "*" 
            ],
            actions=
            ["ecr:GetAuthorizationToken", "ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage", "logs:CreateLogStream", "logs:PutLogEvents"]     
        )
        
        self.pipeline_execution_role.add_to_policy(access_policy_statement)


        task_definition = ECS.FargateTaskDefinition(
            self,"pointcloud-task-description"
            ,execution_role=self.pipeline_execution_role,
            family="pointcloud-reconstruction-task"
        )

        ## NOTE: add workflow for pushing current build container to the ECR repo.
        task_definition.add_container(
            "pointcloud-bacalhau-deployment",
            image=  ECS.ContainerImage.from_registry("devextralabs/pipeline-construction")          
        )
        # for subnet in self.vpc.private_subnets:
        #     self.subnetIds.append(self.vpc.private_subnets)

        bacalhau_api = api_gw.CfnApi(self, id="pipeline-api")
        lambda_role = IAM.Role(self, "lambda-role",
            assumed_by=IAM.ServicePrincipal('lambda.amazonaws.com'),
            role_name = "prod_lambda_role" )
        
        #     lambda_.DockerImageFunction(self, "AssetFunction",
        #     code=lambda_.DockerImageCode.from_image_asset(path.join(__dirname, "docker-handler"))
        # )
        self.viz_lambda = _lambda.DockerImageFunction(
            scope="self",
            id="devextralabs",
            code= _lambda.DockerImageCode.from_image_asset(directory=Path.joinpath( Path.cwd(), "../../packages/3DTileRendererJS/docker/")),
            role=lambda_role,
            vpc=self.vpc
        )
        print(function.connections)
        
