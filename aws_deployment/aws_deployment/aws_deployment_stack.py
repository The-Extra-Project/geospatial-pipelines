from aws_cdk import (
    Stack,
    aws_ecr as ECR,
    aws_ecs as ECS,
    aws_iam as IAM,
    aws_logs as logs,
    aws_ec2 as ec2
)

from constructs import Construct

class AwsDeploymentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        container_service = ECR.Repository(self,id="devextralabs",repository_name="pipeline-pointcloud-reconstruction")

        
        ## now you can use the following possiblities 
        ## 1. defining a new VPC by yourselves (ec2.Vpc)
        ##2. or deploying from the existing VPC's using ec2.Vpc.from_lookup()
        
        vpc = ec2.Vpc(self, "construction-pipeline-vpc")

        ## attaching the cluster layer for the corresponding VPC: 
        
        cluster = ECS.Cluster(self, "extralabs-dev-0.1", cluster_name="pointcoud", vpc=vpc)

        
        pipeline_execution_role = IAM.Role(self, "pipeline-pointcloud-execution-role", assumed_by=IAM.ServicePrincipal("ecs-tasks.amazonaws.com"),role_name="pipeline-running-agent")
        
        
        ## adding the description of the policy statement.
        ## NOTE: here the resources is defined as all of them which are defined based on your role, which at times can be too much permissive. so try to add only the given ARN's
        access_policy_statement = IAM.PolicyStatement(
            effect=IAM.Effect.ALLOW,
            resources=[
                "*" 
            ],
            actions=
            ["ecr:GetAuthorizationToken", "ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage", "logs:CreateLogStream", "logs:PutLogEvents"]
            
        )
        
        pipeline_execution_role.add_to_policy(access_policy_statement)


        task_definition = ECS.FargateTaskDefinition(
            self,"pointcloud-task-description"
            , execution_role=pipeline_execution_role,
            family="pointcloud-reconstruction-task"
        )

        ## NOTE: add workflow for pushing current build container to the ECR repo.
        task_definition.add_container(
            "pointcloud-bacalhau-deployment",
            image=  ECS.ContainerImage.from_registry("devextralabs/extralabs-threed-reconstruction")          
        )
        
        service = ECS.FargateService(self, "point-cloud-service", cluster=cluster, task_definition=task_definition, service_name="devextralabs")
        
        ## checking the logs regarding the deployment / rollback of infrastructure        
        log_group = logs.LogGroup(self, "extralabs-logs", log_group_name="test-reconstruction-pipeline")
