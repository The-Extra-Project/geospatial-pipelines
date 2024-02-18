import openai
from openai import Client
import requests
import logging
import os
import re
from dataclasses import dataclass
import pdal
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
import jsonlib
import tempfile
from subprocess import check_call
"""
this script allows you to:
- Call the assistant API in order to define the given transformation that user wantts to get.
- and then downloads the generated json file from the bot and then execute it.

NOTE: 

- It doesnt work perfectly for the moment and is not reliable enough for production use, 
- Thus use the class PDAL_template_manual instead.

"""
class PDAL_json_generation_template():
    def __init__(self) -> None:
        self.base_prompt = "I want you to generate the pipeline json file based on PDAL(https://pdal.io/en/2.6.0/) latest version of the documentation along with following parameters"    
        self.self_openai_key = os.getenv("OPENAI_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.instructions = """
        You only generate response a pipeline file in JSON format that is to be used by PDAL library (https://pdal.io/en/2.6.0/index.html), given the description of the various parameters like : 
        - writers 
        - readers
        - filters
        - dimensions
        - types 
        etc ... . you should be checking also that the generated JSON file should be correct for execution format so that the given user has to only enter the required parameters in the template.
        also do fill the final generated pipeline with the parameters defined for the translation by the user in the query.
        Also the most important thing is to be aware of first checking whether the given pipeline tasks is feasible or not (i.e whether there exists the given writers , readers and other parameters in order to run the given tasks) and let them know that the query is not correct and rephrase again. 
        """        
    
    def define_assistant_parameter(self, bot_name, associated_file_path: str ):
        """
            this is the one time function call to which you will define the properties like:
            - name
            - instruction prompt
            - model for inference
            - category operation (code interpreter, retriever) etc.
            - additional files (pdal documentation inn pdf) in order provide reference:
                - there can be other details. 
        """
        
        file_id = openai.files.create(
            file=open(associated_file_path, "rb"),
            purpose='assistants'
        )
        print('file uploaded as' + str(file_id.id))
        
        self.assistant = Client.beta.assistants.create(
            name= bot_name,
            instructions= self.instructions,
            file_ids= [str(file_id.id)],
            tools= [
                {"type": "code_interpreter"}
            ],
            model="gpt-4-1106-preview"
        )
        
    
    def creating_message_thread(self, command_description):
        """
        start thread in order to take the user specification and then generate the corresponding pipeline file.
        """

        try:
            message = self.assistant.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=command_description
            )
            thread = Client.beta.threads.create(
                messages=message
            )
            
            run_model = Client.beta.threads.runs.create(
            thread_id= thread.id,
            assistant_id= self.assistant.id)

        except Exception as e:
            print("In the creating_message exception : " + str(e))
        return run_model, thread

    def download_file(self, thread, client:openai.Client):
        try:
            run: openai.beta.threads = client.beta.threads.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                print("messages: ")
                for message in messages:
                    assert message.content[0].type == "text"
                    print({"role": message.role, "message": message.content[0].text.value})

                client.beta.assistants.delete(self.assistant.id)
                print("job is generated , now downloading the generated json spec")
            else:
                print("still in process, check after some time")
        except Exception as e:
            print(" exception in check_status function : " + str(e))
        
        pattern_file = re.search("file-\w+", message.content[0])
        fileId = ''       
        if pattern_file:
            fileid = pattern_file.group(1)

        ## downloading the file to the local container.
        openai.files.content(
            file_id=fileid
        )
        
        return True if fileId is not '' else False
        

@dataclass
class PDAL_template_manual():
    """
    This class consist of the manual defined templates for the user for transformations
    Credits to the lidar2dems and ODM for the references.
    """
    
    def __init__(self):    
        self.pipeline = {'pipeline': []}

    def json_gdal_base(self,filename, output_type, radius, resolution=1, bounds=None):
        """ Create initial JSON for PDAL pipeline containing a Writer element 
        filename : the filename of the output file
        
        """
        json = self.pipeline

        d = {
        'type': 'writers.gdal',
        'resolution': resolution,
        'radius': radius,
        'filename': filename,
        'output_type': output_type,
        'data_type': 'float'
        }

        if bounds is not None:
            d['bounds'] = "([%s,%s],[%s,%s])" % (bounds['minx'], bounds['maxx'], bounds['miny'], bounds['maxy'])
        json['pipeline'].insert(0, d)

        return json

    def generate_cropping_template(self, filename_initial, coordinate_point, distance, output_filename):
        """
        generates the cropping template for then the PDAL to crop the necessary area from the given las file.
        filename_initial : the initial las file name (or path if stored in other place).
        coordinate_point : the coordinate point of the crop area (either by POINT or POLYGON format).
        distance: is the distance of the crop region from the point center thazt is to be considered.
        output_filename : the output filename of the cropped las file
        """
        cropping_template = self.pipeline
        cropping_template['pipeline'].insert(
            0,
            {
               filename_initial
            },
            {
                "type":"filters.crop",
                "bounds": f"{coordinate_point}",
                "distance": f"{distance}"
            },
            {
                "type":"writers.las",
                "filename":{output_filename}
            }        
            
        )   
        return cropping_template

    def add_reader_information(self, filenames_initial):
        """
        adds the reader to one/multiple filenames that're to be read from the given pipeline
        filenames_initial: array of the filenames that are to be integrated in the reader information for the pipeline.
        """
        pipeline  = self.pipeline
        
        if (os.path.splitext(filenames_initial)[1] == 'ply'):
            reader_type = "readers.ply"
        else:
            reader_type = "readers.las"
        
        for files in filenames_initial:
            pipeline.insert(0, {
                "type": f"{reader_type}",
                "filename": files
            })

        return pipeline


    def run_pipeline(generated_json):
        """
        executes the pipeline based on the generated json file for the given transforms
        generated_json: string format of json file which has defined file and reader/writers.
        """
        # create a temporary file to store the pipeline spec and then executed by the PDAL.
        f, jsonfile = tempfile.mkstemp(suffix='.json')
        os.write(f, jsonlib.dumps(generated_json).encode('utf8'))
        os.close(f)
    
        check_call([
                    'pdal',
        'pipeline',
        '-i {}'.format(jsonfile)
        ])    
        


    def merge_pointclouds(input_files, output_file):
        """
        fuses the two point cloud files (based on the common geo-cordinate information s defined in their las header files)
        input_files: array of the input files (in laz format) that are to be merged.
        output_file: the output las file after merge transformation.
        """
        
        assert len(input_files) > 1, "At least two files are required for the merge transformation."
        try:
            check_call([
                'pdal', 'merge', "-f", " ".join(input_files), output_file
            ])

        except Exception as e:
            print("not able to merge point clouds due to the issue: " + str(e))        
    
    
        
        