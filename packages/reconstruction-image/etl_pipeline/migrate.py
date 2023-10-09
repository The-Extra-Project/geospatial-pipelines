"""
migerates the dataset from the storage to S3 with the coordinate metadata , which is to be then parsed by the dataset module of neuralangelo. 
"""

import boto3
#import lib.colmap.scripts.python 
import py7zr
import requests
from subprocess import check_call, Popen, PIPE, STDOUT
import logging
import tqdm
import os
import w3storage

class Migration():
    
    client: boto3.client
    
    
    ## ref from the stackoverflow (to log the process in the subprocess): 
    
    def log_subprocess_output(pipe):
        for line in iter(pipe.readline, b''): # b'\n'-separated lines
            logging.info('got line from subprocess: %r', line)
    
    def __init__(self, bucket_name,url,w3_storage_token,region):
        self.client = boto3.client('s3', region_name=region)
        self.bucket_name = bucket_name  #(if the object folder is already created, the accessible bucketname for the given user)
        self.url = url
        self.w3 = w3storage.API(token=w3_storage_token)
    
    
    def get_size(self,folder_name):
        total_size =0
        for _file in self.client.list_objects(
            Bucket=self.bucket_url, Prefix=folder_name)["Contents"]:
            total_size += _file["Size"]
            return total_size
    
        
               
    def transfer_data(self,folder_name, storage_type, **kwargs):
        os.mkdir(folder_name)
        os.chdir(folder_name)
        dataset_download = requests.get(self.url, stream=True)
        ## download the dataset from curl with specific folder for the output
        check_call(['curl', self.url, '-o', 'neuralangelo_dataset.7z'])
        ## extract the dataset from the 7z file
        with py7zr.SevenZipFile('neuralangelo_dataset.7z', mode='r') as z:
            z.extractall()
        os.chdir('../')
        
        if storage_type == "AWS":
            try:
            ## upload the folder extracted in the previous step to the S3 bucket
                upload_size = self.get_size(folder_name=folder_name)
                with tqdm.tqdm(total=upload_size, unit="B", unit_scale=True, desc=folder_name) as pbar:
                    self.client.upload_file(
                    folder_name, 
                    self.bucket_name, folder_name, Callback= lambda bytes_transferred: pbar.update(bytes_transferred))
            
            except Exception as e:
                print(e)
    
        elif storage_type == "ipfs":
            upload_size= self.get_size(folder_name)
            for _file in os.listdir(path="./"+folder_name):
                self.w3.post_upload(_file)
            
    def run_colmap_transformations(self,directory):
        """
        Runs the colmap transformations on the given dataset of the images.
        directory: is the relative path of the dataset directory (given from the output dataset) which is also the project path.
        
        """   
       
        self.process = check_call(["colmap", "feature_extractor", "--database_path="+ directory +"/database.db", "--image_path="+ directory +"/images_raw"], stdout=PIPE, stderr=STDOUT) #Popen('./run_colmap.sh', directory, stdout=PIPE, stderr=STDOUT)
        with self.process.stdout:
            self.log_subprocess_output(self.process.stdout)
        exitcode = self.process.wait()
        print('exit code:'+ exitcode)
        
        
        
if __name__ == "__main__":
    migration = Migration('neuralangelo-dataset', 'https://www.eth3d.net/data/multi_view_training_dslr_undistorted.7z', w3_storage_token='', region ='us-east-1')
    migration.run_colmap_transformations('./eth_dataset')                  
                    
        