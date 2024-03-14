FROM python as base

WORKDIR app/

COPY requirements.txt ./app/requirements.txt
RUN pip install -r ./app/requirements.txt 
COPY . . 
ENTRYPOINT [ "pytest", "./test/unit/test_camera_utils.py"  ]



