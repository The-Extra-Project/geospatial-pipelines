from setuptools import setup, find_packages
import os

def read(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    file = open(filepath, 'r')
    return file.read()

setup(
    name='geospatial-pipelines',
    author="Dhruv Malik",
    version='0.1.0',
    author_email="dhruv@extralabs.xyz",
    description="scripts for allowing user to load and preprocess data from the lidar / image data in order to convert into raw attributed point cloud dataset",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)

