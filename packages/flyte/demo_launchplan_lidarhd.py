"""
example for testing the concept of the launchplan for running the reocnstruction jobs with the by default parameters.
for instance, running the reconstruction parameters on the reconstruction of the format for the given region after some epochs.
"""
import os
from bs4 import BeautifulSoup

laz_file_paths_rochfort = [
"https://storage.sbg.cloud.ovh.net/v1/AUTH_63234f509d6048bca3c9fd7928720ca1/ppk-lidar/FK/LHD_FXX_0392_6546_PTS_O_LAMB93_IGN69.copc.laz",
"https://storage.sbg.cloud.ovh.net/v1/AUTH_63234f509d6048bca3c9fd7928720ca1/ppk-lidar/FK/LHD_FXX_0393_6546_PTS_O_LAMB93_IGN69.copc.laz",
"https://storage.sbg.cloud.ovh.net/v1/AUTH_63234f509d6048bca3c9fd7928720ca1/ppk-lidar/FK/LHD_FXX_0393_6545_PTS_O_LAMB93_IGN69.copc.laz",
"https://storage.sbg.cloud.ovh.net/v1/AUTH_63234f509d6048bca3c9fd7928720ca1/ppk-lidar/FK/LHD_FXX_0392_6545_PTS_O_LAMB93_IGN69.copc.laz",
"https://storage.sbg.cloud.ovh.net/v1/AUTH_63234f509d6048bca3c9fd7928720ca1/ppk-lidar/FK/LHD_FXX_0391_6546_PTS_O_LAMB93_IGN69.copc.laz",
"https://storage.sbg.cloud.ovh.net/v1/AUTH_63234f509d6048bca3c9fd7928720ca1/ppk-lidar/FK/LHD_FXX_0392_6547_PTS_O_LAMB93_IGN69.copc.laz",
"https://storage.sbg.cloud.ovh.net/v1/AUTH_63234f509d6048bca3c9fd7928720ca1/ppk-lidar/FK/LHD_FXX_0393_6547_PTS_O_LAMB93_IGN69.copc.laz"
]

import pymysql as mysql
import requests
from subprocess import check_call
from flytekitplugins.bacalhau import BacalhauTask, BacalhauAgent
from flytekit import LaunchPlan, task, workflow, kwtypes
from typing import List
from pathlib import Path



# with mysql.connection(host="localhost", user="root", password=os.getenv("DB_PASSWD"), database=os.getenv("DB_DATABASE")) as conn:
#     with conn.cursor() as cursor:
#         cursor.execute("USE circum")
#         cursor.execute("CREATE TABLE IF NOT EXISTS lidarhd_files lidarhd_files VARCHAR(255), file_name VARCHAR(255), ipfs")

class LidarHdParser():
    base_url: str = os.getenv("BASE_URL")
    
    def __init__(self):
        self.bacalhau_task = BacalhauTask(
                name="lidarhd_extraction_pipeline",
                inputs=kwtypes(
                    spec=dict,
                    api_version=str,
                ),
            )
        
        self.spec = dict(
            engine="Docker",
            verifier="Noop",
            PublisherSpec={"type": "IPFS"},
            docker={
                "image": "ubuntu",
                "entrypoint": ["echo", "Flyte is awesome!"],
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
        )
    
    @task
    def parsing_tabular_format(self):
        try:
            base_dir = requests.get(self.base_url)
            assert base_dir.raise_for_status() is None
            parser = BeautifulSoup(base_dir.content, "html.parser")
            
            table = parser.find("table", id="listing")
            if not table:
                return []
            # Extract data from table rows
            file_data = []
            for row in table.find_all('tr')[1:]:  # Skip the heading row
                data_cells = row.find_all('td')
                if len(data_cells) == 3:  # Check for expected number of columns
                    file_data.append({
                    "name": data_cells[0].text.strip(),
                    "size": data_cells[1].text.strip(),
                    "date": data_cells[2].text.strip()
                    })
            return file_data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    def download_point_cloud_city(self, city_name: str, file_paths: List[str]):
        """
        runs the job to download the point cloud files from the given city 
        (given that either we do have  the attribution between the city and the given infrastructure).
        city_name: str, the name of the city
        file_paths: List[str], the list of the file paths to download.        
        """
        current_dir = os.getcwd()
        counter = 0
        if not os.path.exists(current_dir + "/" + city_name + "_files"):
            os.makedirs(city_name + "_files")
            os.chdir(city_name)
            for i in file_paths:
                check_call(["wget", i , "-U" , "'User-Agent': 'Mozilla/5.0'",  "-O", "rochefort_files_" + str(counter) + ".copc.laz"])
                counter += 1
                





# @workflow

# launchplan_epoch = LaunchPlan.get_or_create(
#     workflow=run_downloading_compute_job,
#     name="launchplan_epoch",
#     default_inputs={"laz_paths":laz_file_paths},
# )

# if __name__ == "__main__":
#     run_downloading_compute_job(laz_file_paths, "rochefort")


