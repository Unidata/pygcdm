# pygcdm
[![Coverage Status](https://coveralls.io/repos/github/rmcsqrd/netcdf-grpc/badge.svg?branch=coveralls)](https://coveralls.io/github/rmcsqrd/netcdf-grpc?branch=coveralls)

A python API for transferring [Common Data Model (CDM)](https://docs.unidata.ucar.edu/netcdf-java/current/userguide/common_data_model_overview.html) files using [Remote Procedure Calls](https://grpc.io/).

## Installation
Create a new virtual environment using [conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands). If you don't have `conda` installed on your machine, install if following [these instructions](https://conda.io/projects/conda/en/latest/user-guide/install/index.html). Note that `pygcdm` requires `python>=3.9` so we specify that explicitly. We can then use `pip` for installation after activating the `conda` environment.
```
conda create --name [environment name] python=3.9
conda activate [environment name]
pip install pygcdm
```

## Usage

### Transfer Files using gRPC
This demonstrates how to implement the python encode/decode API and transmit netCDF files via gRPC. Start by opening up two separate tabs in your terminal. Make sure that whatever python environment you installed the requirements into is active in both. Navigate to the `examples` folder in this repo. 

In the first tab, start the gRPC server by running the following command:
```
python grpc_netcdf_server.py
```
If it is working properly you should see something that says `starting server...`.

In the second tab, make a client request by running the following command:
```
python grpc_netcdf_client.py
```
Something resembling an xarray dataset should print to the terminal if everything is working. Feel free to modify the `loc` and `variable_spec` variables in `grpc_netcdf_client.py` to modify what data is transmitted.

### Encode/Decode API
This demonstrates how to encode/decode gRPC messages within a python shell:
```
# import/instantiate encoder object
from pygcdm.netcdf_encode import netCDF_Encode
encoder = netCDF_Encode()

# import and define header request
import pygcdm.protogen.gcdm_netcdf_pb2 as grpc_msg
file_loc = "test/data/test3.nc"
header_request = grpc_msg.HeaderRequest(location=file_loc)
header_response = encoder.generate_header_from_request(header_request)

# define data request
var_spec = "analysed_sst"
data_request = grpc_msg.DataRequest(location=file_loc, variable_spec=var_spec)
data_response = encoder.generate_data_from_request(data_request)

# decode header/data into xarray object
from pygcdm.netcdf_decode import netCDF_Decode
decoder = netCDF_Decode()
ds = decoder.generate_file_from_response(header_response, data_response)
```

## Utilities

### Rebuilding the Package Locally
If you modify the package locally and want to rebuild the package for testing you can run the following command from the root folder:
```
pip install .
```
(You can verify installation by running `pip show -f pygcdm`).

### Committing the Package to PyPi
If you have the priviledges to do so, you can commit the package to PyPi by running the following command in the root folder:
```
python setup.py upload
```
which will prompt you what type of upload you want: `test` or `real`, where `test` uploads to [https://test.pypi.org/project/pygcdm/](https://test.pypi.org/project/pygcdm/) and `real` uploads to [https://pypi.org/project/pygcdm/](https://pypi.org/project/pygcdm/). You'll then be prompted to include your login credentials. 

### Generating Python Source Code from `proto` Files
In order to generate the grpc python source code from the `.proto` files in `protos/src/protogen`, we need to use the `protoc` compiler (the reason for the weird subfolder structure is so that `protoc` generates files with proper import namespaces). The python package with `protoc` can be installed by following the instructions [here](https://www.grpc.io/docs/languages/python/basics/#generating-client-and-server-code).

To compile our code, and put the resulting functions into `src/protogen/`, we can use the following commands (from the root directory where this README is located):
```
$ python -m grpc_tools.protoc -I protos/ --python_out=. --grpc_python_out=. protos/pygcdm/protogen/*.proto
```

More information on the `protoc` compiler can be found by loading the module in python and using the `help` command:
```
$ python
>>> import grpc_tools.protoc
>>> help(grpc_tools.protoc)
```

### Run tests locally
If you want to run the tests locally, make sure you have the `pytest` module installed. Then, from the root directory run the following command:
```
pytest test/*.py
```
If you are testing to verify any changes make sure you rebuild the package locally using the instructions above.
