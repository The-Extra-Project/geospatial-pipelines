import requests
import pytest
from fastapi.testclient import TestClient
from fastapi import Body
from bacalhau.job_scheduler import app

client = TestClient(app)


details_model_config = { 
    
    "jobspec": {
    "storage_files_path": "../reconstruction_image/neuralangelo_modified/datas"}
    }
#@pytest.mark.asyncio
def test_schedule_job():
   
   image_param = "../reconstruction_image/neuralangelo_modified/datas"
   input_params = {
        "jobspecdocker": {
            "image": "devextralabs/dockerfile-colmap:latest",
            "command": [image_param]
        }
    }
   try:
    response =  client.post("/bacalhau/neuralangelo/submit",json=input_params)
   except Exception as e:
       print(e)
   assert response.status_code == 200
   response_json = response.json()
   assert response_json["message"] is not None

   print(response.content)