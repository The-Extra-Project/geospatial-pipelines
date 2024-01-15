from flytekit import workflow, tasks, kwtypes, dynamic
from flytekitplugins.bacalhau import BacalhauTasks
from bacalhau_apiclient.odels.all_of_job_spec import Spec
import asyncio
import json
from typing import List
import logging

logging.getLogger(__file__)

class GeospatialPipelineTaskQueue:
    """
    Its the wrapper on top of flyteplugins that:
    - Creates the task corresponding to the given user and adds them into the queue.
    - based on the status being active or stale, users cna remove certain tasks from the queue also
    - Then runs the task based on the given specification of the job input as the FIFO.
    """
    workflow_tasks_object: List(BacalhauTasks)
    workflow_current: int   
    tasks_queue:any
    
    def __init__(self):
        self.version = "v0.1"
        self.tasks_queue = asyncio.Queue()
        
    def read_pipeline_spec(self, json_file: str):
        """
        function that reads the json file to get the description of the pipeline that are to be run.
        this will then be used to  put the input in order to schedule the operations.        
        Json_file: Its the reference file path that is to be read in order to decide the execution steps of the given geospatial transformation.       
        """
        file_details = json.dumps(json_file, indent=4)
        return file_details

    async def enqueue_task(self,_name: str):
        """
        defines the flyte tasks in order to execute and generate the results.
        _name: its the name of the workflow task that needs to be executed.
        """
        
        task = BacalhauTasks(
        name= _name,
        inputs=kwtypes(
            spec=dict,
            api_version=self.version
        )        
        )
        enque_id = await self.tasks_queue.put(task)        

        return  enque_id
    @tasks
    async def dequeue_task(self):
        """
        this will dequque the latest task from the given job queue and run it on the flyte workflow.
        """
        dequed_task = await self.tasks_queue.get()
        if dequed_task is None:
            exit
        return dequed_task        
    
    @workflow
    async def workflow_execution(self,specs_json):
        """
        this function runs all of the tasks that are stored in the queue by running the enqueing the tasks one by one.
        specs_json are the json specifications of the bacalhau that are to be executed with the deququed operation
        """
        
        while True:
            task_queue = await self.dequeue_task()
            if task_queue is None:
                break
            task = task_queue(
                api_version = self.version,
                spec = dict(specs_json)
            )

            print(task)


def main():
    ## gives the various tasks to be executed in the project.
    ## credits to the example from bacalhau flyte project.
    
    specs_json = [

            dict( engine="Docker",
            verifier="Noop",
            PublisherSpec={"type": "IPFS"},
            docker={
                "image": "ubuntu",
                "entrypoint": ["echo", "Flyte is awesome and with Bacalhau it's even better!"],
            },
            language={"job_context": None},
            wasm=None,
            resources=None,
            timeout=1800,
            outputs=[
                {
                    "storage_source": "IPFS",
                    "name": "outputs",
                    "path": "/outputs",
                }
            ],
            deal={"concurrency": 1},
            ),

            dict(
            engine="Docker",
            verifier="Noop",
            PublisherSpec={"type": "IPFS"},
            docker={
                "image": "ubuntu",
                "entrypoint": ["cat", "/myinputs/stdout"],
            },
            language={"job_context": None},
            wasm=None,
            resources=None,
            timeout=1800,
            outputs=[
                {
                    "storage_source": "IPFS",
                    "name": "outputs",
                    "path": "/outputs",
                }
            ],
            inputs=[
                {
                    "cid": specs_json[0],
                    "name": "myinputs",
                    "path": "/myinputs",
                    "storageSource": "IPFS",
                }
            ],
            deal={"concurrency": 1},
        )
    ]
    
    tasks = GeospatialPipelineTaskQueue()
    
    tasks.enqueue_task("task_1")
    tasks.enqueue_task("task_2")
    
    tasks.workflow_execution(specs_json=specs_json)
    



if __name__ == "__main__":
    main()
    