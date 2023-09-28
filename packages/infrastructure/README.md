
# template for deploying your reconstruction pipeline on cloud: 



## Build/deployment steps

1. Setting up the virtual enviornment:
```
$ python3 -m venv .venv
```
2.  After the init process completes and the virtualenv is created, you can use the following step to activate your virtualenv.

```
$ source .venv/bin/activate
```

3. Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

4. Add the envionment variables in '.aws/.env' file, defining your account identifier and access token instructions. 




5. run the script for deploying the container service with required parameters.

```
$ python app.py
```

6. To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.
