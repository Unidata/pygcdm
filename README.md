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
This demonstrates how to implement the python encode/decode API and transmit netCDF files via gRPC. Start by opening up two separate tabs in your terminal. Make sure that whatever python environment you installed the requirements into is active in both. 

BONE sign off need to figure out this stupid module issues 


