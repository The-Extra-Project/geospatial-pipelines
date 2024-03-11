import streamlit as st
import requests
import os
import uuid
import leafmap.foliumap as leafmap
from  bacalhau_sdk import api, config
from bacalhau_apiclient import models
from bacalhau_apiclient.models.job_spec_language import JobSpecLanguage
from bacalhau_apiclient.models.storage_spec import StorageSpec
import time
import boto3
from bacalhau_apiclient.models.job_spec_docker import JobSpecDocker
from bacalhau_apiclient.models.publisher_spec import PublisherSpec
from bacalhau_apiclient.models.deal import Deal
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import datetime
load_dotenv()
base_url_lidarhd = os.getenv("BASE_URL_LIDARHD")
access_id = os.getenv("AWS_ACCESS_ID")
account_key = os.getenv("AWS_ACCESS_KEY")


## following functions  are from the S3 bucket (in order to store the large operation files)

def scrape_file_info(url):
    """
    Scrapes file information (name, size, date) from an HTML directory listing.
    Args:
        url: The URL of the directory listing page.

    Returns:
        A list of dictionaries, where each dictionary contains information for a file:
            - name: The filename.
            - size: The file size.
            - date: The last modified date.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for non-200 status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table element containing the file listings
        table = soup.find('table', id='listing')
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

def upload_to_s3(s3_client, bucket_name, url, filename, metadata):
    """
    uploads the data to the S3 storage.
    s3_client: its the boto S3 object with the credentials in order to upload the file
    
    """
    try:
        # Download the necessary files
        file_data = scrape_file_info(url)
        for file_detail in file_data: 
            response = requests.get(url + '/' + file_data[file_detail].name, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
        # Upload to S3 
            s3_client.upload_client(response.raw, bucket_name, filename, ExtraArgs=metadata)
            st.write(f"Uploaded file: {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")

    
    

base_pipeline_spec =  dict(
            engine="Docker",
            verifier="Noop",
            PublisherSpec={"type": "IPFS"},
            docker={
                "image": "",
                "entrypoint": [],
            },
            language={"job_context": None},
            wasm=None,
            resources=None,
            timeout=7200,
            outputs=[
                {
                    "storage_source": "IPFS",
                    "name": "outputs",
                    "path": "/outputs",
                }

            ],
            deal={"concurrency": 1},
        )



pdal_pipeline_spec = ""

pipeline = ["devextralabs/neuralangelo","devextralabs/surface_reconstruction", "devextralabs/georender"]

##bacalhau_parameters = GeospatialPipelineTaskQueue()

st.session_state.reconstruction_algorithm = None

## only to be used for debugging the bacalhau deployments
data_demo = dict(
    APIVersion='V1beta1',
    ClientID=config.get_client_id(),
    Spec=models.Spec(
        engine="Docker",
        verifier="Noop",
        publisher_spec=PublisherSpec(type="IPFS"),
        docker=JobSpecDocker(
            image="ubuntu",
            entrypoint=[ "echo", "python cropping.py --input_file /inputs/bunny.pcd --coordinates [7,10,9,12,0,3] --reference_point (0,0,0)" ],
        ),
        language=JobSpecLanguage(job_context=None),
        wasm=None,
        resources=None,
        timeout=1800,
        outputs=[
            StorageSpec(
                storage_source="IPFS",
                name="outputs",
                path="/outputs",
            )
        ],
        deal=Deal(concurrency=1, confidence=0, min_bids=0),
        do_not_track=False,
    ),
)



def reconstruction_dashboard():
    st.title("circum:- scheduling compute job")
    
    
    algorithm_category = st.selectbox("Select the algorithm", options=["cropping","surface_reconstruction","reconstruction using nerf's", "data migration"])
    choice = st.selectbox(label="select the option",options=("via 3D coordinates", "via 2D coordinates"))
    if algorithm_category == "poisson_SR":
        poisson_SR_dashboard()

    if algorithm_category == "data_migration":
        bucket_params = st.write('enter the S3 bucket name where the data is to be migrated')
        

    if choice == "via 2D coordinates":
        st.write("enter the point of interest (in WGS 84 standard)")
        X_coord = st.number_input("X coordinate", min_value=1)
        Y_coord = st.number_input("Y coordinate", min_value=1)
        base_pipeline_spec["docker"]["image"] = pipeline[1]
        points = [X_coord, Y_coord]
        base_pipeline_spec["docker"]["entrypoint"].append(["python", "cropping.py", "--points", points, "--username",'st.session_state.email' ])
        execute = st.button("run the pipeline")
        
        params = dict(
        APIVersion='v0.1',
        ClientID=config.get_client_id(),
        Spec= models.Spec(base_pipeline_spec)
        )

        if execute:
            submit_job = api.submit(data_demo)
            st.write(f"""running the pipeline with the following parameters""")
            st.json(data_demo)
            jobId = submit_job.job.metadata.id
            st.info(f"job_id generated from the user:{jobId}" )
            resulting_output = api.results(jobId)
            file_details = './output/' + jobId + 'cropped.pcd' 
            while time.sleep(5):
                pass
                
            st.success(f"""the computed wresulting file: {file_details}""" )
            
    if choice == "via 3D coordinates":
        st.write("enter the point of interest (in WGS 84 standard)")
        X = st.text_input("Xmax & min coord(using comma)")
        Y= st.text_input("Ymax & min coord(using comma)")
        Z= st.text_input("Zmax & min coord(using comma)")
        
        base_pipeline_spec["docker"]["image"] = pipeline[1]
        points = [X, Y, Z]
        base_pipeline_spec["docker"]["entrypoint"].append(["python", "cropping.py", "--points", points, "--username",'st.session_state.email' ])
        execute = st.button("run the pipeline")
        
        params = dict(
        APIVersion='v0.1',
        ClientID=config.get_client_id(),
        Spec= models.Spec(base_pipeline_spec)
        )
        if execute:
            submit_job = api.submit(data_demo)
            st.write(f"""running the pipeline with the following parameters""")
            st.json(data_demo)
            jobId = submit_job.job.metadata.id
            st.info(f"job_id generated from the user:{jobId}" )
            resulting_output = api.results(jobId)
            file_details = './output/' + jobId + '/cropped_demo.pcd' 
            while time.sleep(5):
                pass
                
            st.success(f"""the computed wresulting file: {file_details}""" )

def poisson_SR_dashboard():
    with st.container():
        st.write("running the pipeline for application of poisson surface reconstruction")
        st.write(base_pipeline_spec)


reconstruction_dashboard()
## 
## documents
## 7,10 , 9 , 12 , 0 , 3