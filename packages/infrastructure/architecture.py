from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS, ECR
from diagrams.aws.network import VPC
from diagrams.saas.chat import Discord
from diagrams.saas.social import Twitter
from diagrams.generic.compute import Rack


with Diagram("pipeline workflow"):
    client = [Discord("discord client"), Twitter("twitter client")] 
    with Cluster("pipeline execution"):
        sector = VPC("subnet")
        ecs_service = ECS("")
        compute_registry = ECR("container reg")
        client >> sector >> ecs_service >> compute_registry
    
    with Cluster("bacalhau compute framework"):
        compute_registry >> Rack("requester node") >> [
            Rack("compute node 1"), Rack("compute node 2")
        ]
    
    
    




