import pytest
from pygcdm.netcdf_encode import netCDF_Encode
import pygcdm.protogen.gcdm_netcdf_pb2 as grpc_msg
from pygcdm.netcdf_decode import netCDF_Decode
import xarray as xr
import netCDF4 as nc4

def test_class_error_handling():
    encoder = netCDF_Encode()
    decoder = netCDF_Decode()

    ## HEADER FILE TESTS
    # error: not a HeaderRequest
    response = encoder.generate_header_from_request(None)
    assert response.error.message == 'Message sent is not of type HeaderRequest'

    # error: file does not exist
    msg = grpc_msg.HeaderRequest(location="obviously/not/a/file")
    response = encoder.generate_header_from_request(msg)
    assert response.error.message == 'Specified file path does not exist'

    # error: file does not exist
    msg = grpc_msg.HeaderRequest(location="test/data/notncfile.txt")
    response = encoder.generate_header_from_request(msg)
    assert response.error.message == 'Specified file is not a netCDF file'

    ## DATA FILE TESTS
    # error: not a DataRequest
    response = encoder.generate_data_from_request(None)
    assert response.error.message == 'Message sent is not of type DataRequest'

    # error: file does not exist
    msg = grpc_msg.DataRequest(location="obviously/not/a/file")
    response = encoder.generate_data_from_request(msg)
    assert response.error.message == 'Specified file path does not exist'

    # error: file does not exist
    msg = grpc_msg.DataRequest(location="test/data/notncfile.txt")
    response = encoder.generate_data_from_request(msg)
    assert response.error.message == 'Specified file is not a netCDF file'

    # error: general bad var_spec
    msg = grpc_msg.DataRequest(location="test/data/test3.nc",
                               variable_spec="not_analysed_sst" 
                               )
    response = encoder.generate_data_from_request(msg)
    assert response.error.message == 'Incorrect variable spec: specified variable does not exist'

    # error: bad var_spec variable
    msg = grpc_msg.DataRequest(location="test/data/test3.nc",
                               variable_spec="not_analysed_sst" 
                               )
    response = encoder.generate_data_from_request(msg)
    assert response.error.message == 'Incorrect variable spec: specified variable does not exist'

def test_grpc_error_reporting():
    pass
