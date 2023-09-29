import pytest
from subprocess import check_call
"""
here we will test the surface_reconstruction with docker build, so run this script only via the test script
"""

input_las_file=""
algorithm_flag=0 

url = "localhost:8081"

def run_cgal_surface_reconstruction_algorithm():
    status = check_call([
        "docker", "run" , "--rm", "-v ../packages/georender/data:/data", input_las_file, algorithm_flag,
    ])
    
    assert status is not None
    
    
    
    
    
def run_cgal_surface_reconstruction_algorithm_with_recon():
    """
    this will be for testing multi adaptive solver algorithm
    """
    
    algorithm_flag=2
    
    status = check_call([
        "docker", "run" , "--rm", "-v ../packages/georender/data:/data", input_las_file, algorithm_flag,
    ])

    assert status is not None
    
    
