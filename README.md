# pygcdm
[![Coverage Status](https://coveralls.io/repos/github/rmcsqrd/pygcdm/badge.svg?branch=main)](https://coveralls.io/github/rmcsqrd/pygcdm?branch=main)
[![PyPI](https://img.shields.io/pypi/v/pygcdm)](https://pypi.org/project/pygcdm/)

A python API for transferring [Common Data Model (CDM)](https://docs.unidata.ucar.edu/netcdf-java/current/userguide/common_data_model_overview.html) files using [Remote Procedure Calls](https://grpc.io/).

- [Installation](#install)
- [Usage](#use)
  - [Transfer Files using GRPC](#transferAPI)
  - [Encode/Decode API](#encodedecode)
  - [Message Types](#msgtypes)
  - [`variable_spec` Definition](#varspecdef)
- [Utilities](#util)
  - [Rebuilding the Package Locally](#buildlocal)
  - [Committing the Package to PyPi](#buildpypi)
  - [Generating Python Source Code from `proto` Files](#genproto)
  - [Run Tests Locally](#runtests)

## Installation<a name="install"></a>
Create a new virtual environment using [conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands). If you don't have `conda` installed on your machine, install if following [these instructions](https://conda.io/projects/conda/en/latest/user-guide/install/index.html). Note that `pygcdm` requires `python>=3.9` so we specify that explicitly. We can then use `pip` for installation after activating the `conda` environment.
```
conda create --name [environment name] python=3.9
conda activate [environment name]
pip install pygcdm
```

## Usage<a name="use"></a>

### Transfer Files using gRPC<a name="transferAPI"></a>
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

### Encode/Decode API<a name="encodedecode"></a>
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

### Message Types<a name="msgtypes"></a>
`pygcdm` has two message types `HeaderRequest` and `DataRequest` which have corresponding response types (`HeaderResponse`, `DataResponse` respectively). These messages can be learned about [here](https://grpc.io/docs/what-is-grpc/introduction/#working-with-protocol-buffers) and are defined in `protos/pygcdm/protogen/gcdm_netcdf.proto`. The main idea is that you pack your request messages with the information you want and unpack the response messages (`pygcdm` does this packing/unpacking for you). The `.proto` messages are pretty human readable but a description is provided here:

`HeaderRequest`:
- `location` (string): file location where netCDF file is found on machine delivering response

`DataRequest`:
- `location` (string): file location where netCDF file is found on machine delivering response
- `variable_spec` (string): desctribes what netCDF variable/variable slices you want to request (see `variable_spec` section in this README)

### `variable_spec` Definition<a name="varspecdef"></a>
`variable_spec` is how you define which variable/data slices you want from the remote netCDF file. It follows [Backus-Naur form](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form) according to the following definition, which was adopted from `netcdf-java` which is documented [here](https://docs.unidata.ucar.edu/netcdf-java/7.0/javadoc/ucar/nc2/ParsedArraySectionSpec.html):
```
section specification := selector | selector '.' selector
selector := varName ['(' dims ')']
varName := ESCAPED_STRING


dims := dim | dim, dims
dim := ':' | slice | start ':' end | start ':' end ':' stride
slice := INTEGER
start := INTEGER
stride := INTEGER
end := INTEGER
ESCAPED_STRING : must escape characters = ".("
```
In practice, this means that `variable_spec` can look like the following examples. Slicing notation is analogous to numpy slicing (but not identical).
- `analysed_sst` 
- `analysed_sst(:, :, :)`
- `analysed_sst(0,0:719:10,0:1439:10)`
- `analysed_sst(0,200:700:10,1300:1400:10)`

Note that these examples are derived from some of the tests in `test/`. 


## Utilities<a name="util"></a>

### Rebuilding the Package Locally<a name="buildlocal"></a>
If you modify the package locally and want to rebuild the package for testing you can run the following command from the root folder:
```
pip install .
```
(You can verify installation by running `pip show -f pygcdm`).

### Committing the Package to PyPi<a name="buildpypi"></a>
If you have the privileges to do so, you can commit the package to PyPi by running the following command in the root folder:
```
python setup.py upload
```
which will prompt you what type of upload you want: `test` or `real`, where `test` uploads to [https://test.pypi.org/project/pygcdm/](https://test.pypi.org/project/pygcdm/) and `real` uploads to [https://pypi.org/project/pygcdm/](https://pypi.org/project/pygcdm/). You'll then be prompted to include your login credentials. 

### Generating Python Source Code from `proto` Files<a name="genproto"></a>
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

### Run Tests Locally<a name="runtests"></a>
If you want to run the tests locally, make sure you have the `pytest` module installed. Then, from the root directory run the following command:
```
pytest test/*.py
```
If you are testing to verify any changes make sure you rebuild the package locally using the instructions above.
