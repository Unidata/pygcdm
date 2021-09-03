# netcdf-grpc

## Usage

#### Encode/Decode API
This demonstrates how to encode/decode gRPC messages within a python shell:
```
# import/instantiate encoder object
from src.netcdf_encode import netCDF_Encoder
encoder = netCDF_Encode()

# import and define header request
import src.proto_gen.gcdm_netcdf_pb2 as grpc_msg
file_loc = "test/data/test.nc"
header_request = grpc_msg.HeaderRequest(location=file_loc)
header_response = encoder.GenerateHeaderFromRequest(header_request)

# define data request
data_request = grpc_msg.DataRequest(location=file_loc, variable_spec=var_spec)
data_response = encoder.GenerateDataFromRequest(data_request)

# decode header/data into xarray object
from src.netcdf_decode import netCDF_Decode
decoder = netCDF_Decode()
ds = decoder.GenerateFileFromResponse(header_response, data_response)
```

#### Transfer Files using gRPC
This demonstrates how to implement the python encode/decode API and transmit netCDF files via gRPC. Start by opening up two separate tabs in your terminal. Make sure that whatever python environment you installed the requirements into is active in both. Make sure that you are in base folder of this repo. 

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

## Generating Python Source Code from `proto` Files
In order to generate the grpc python source code from the `.proto` files in `protos/src/protogen`, we need to use the `protoc` compiler (the reason for the weird subfolder structure is so that `protoc` generates files with proper import namespaces). The python package with `protoc` can be installed by following the instructions [here](https://www.grpc.io/docs/languages/python/basics/#generating-client-and-server-code).

To compile our code, and put the resulting functions into `src/protogen/`, we can use the following commands (from the root directory where this README is located):
```
$ python -m grpc_tools.protoc -I protos/ --python_out=. --grpc_python_out=. protos/src/protogen/*.proto
```

More information on the `protoc` compiler can be found by loading the module in python and using the `help` command:
```
$ python
>>> import grpc_tools.protoc
>>> help(grpc_tools.protoc)
```
