import pytest
from pygcdm.netcdf_encode import netCDF_Encode
import pygcdm.protogen.gcdm_netcdf_pb2 as grpc_msg
from pygcdm.netcdf_decode import netCDF_Decode
import xarray as xr
import netCDF4 as nc4

def test_class_error_handling():
    encoder = netCDF_Encode()
    decoder = netCDF_Decode()

    # test encoder/decoder message error handling
    try:
        encoder.generate_header_from_request(None)
    assert type(ds) == xr.Dataset  # ensure that dataset is correct
    assert (ds.variables[var_spec][:].data == nc.variables[var_spec][:]).all()  # check if data matches

def test_grpc_error_reporting():
    pass
