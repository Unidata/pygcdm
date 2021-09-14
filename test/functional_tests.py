import pytest
from pygcdm.netcdf_encode import netCDF_Encode
import pygcdm.protogen.gcdm_netcdf_pb2 as grpc_msg
from pygcdm.netcdf_decode import netCDF_Decode
import xarray as xr
import netCDF4 as nc4

def test_encode_decode():

    # test encode/decode: entire variable
    encoder = netCDF_Encode()
    decoder = netCDF_Decode()
    file_loc = 'test/data/test3.nc'
    var_spec = 'analysed_sst'
    header_request = grpc_msg.HeaderRequest(location=file_loc)
    header_response = encoder.generate_header_from_request(header_request)
    data_request = grpc_msg.DataRequest(location=file_loc, variable_spec=var_spec)
    data_response = encoder.generate_data_from_request(data_request)
    ds = decoder.generate_file_from_response(header_response, data_response)
    nc = nc4.Dataset(file_loc)
    nc.set_auto_maskandscale(False)

    assert type(ds) == xr.Dataset  # ensure that dataset is correct
    assert (ds.variables[var_spec][:].data == nc.variables[var_spec][:]).all()  # check if data matches

    # test encode/decode: entire variable via slicing
    encoder = netCDF_Encode()
    decoder = netCDF_Decode()
    file_loc = 'test/data/test3.nc'
    var_spec = 'analysed_sst(:,:,:)'
    header_request = grpc_msg.HeaderRequest(location=file_loc)
    header_response = encoder.generate_header_from_request(header_request)
    data_request = grpc_msg.DataRequest(location=file_loc, variable_spec=var_spec)
    data_response = encoder.generate_data_from_request(data_request)
    ds = decoder.generate_file_from_response(header_response, data_response)
    nc = nc4.Dataset(file_loc)
    nc.set_auto_maskandscale(False)
    var_name, slices = encoder._interpret_var_spec(var_spec)
    section = encoder._interpret_slices(slices, nc.variables[var_name].get_dims())

    assert type(ds) == xr.Dataset  # ensure that dataset is correct
    assert (ds.variables[var_name][:].data == nc.variables[var_name][encoder.interpret_section(section)]).all()  # check if data matches

    # test encode/decode: entire variable via arbitrary slicing
    encoder = netCDF_Encode()
    decoder = netCDF_Decode()
    file_loc = 'test/data/test3.nc'
    var_spec = 'analysed_sst(0,100:200,500:1301)'
    header_request = grpc_msg.HeaderRequest(location=file_loc)
    header_response = encoder.generate_header_from_request(header_request)
    data_request = grpc_msg.DataRequest(location=file_loc, variable_spec=var_spec)
    data_response = encoder.generate_data_from_request(data_request)
    ds = decoder.generate_file_from_response(header_response, data_response)
    nc = nc4.Dataset(file_loc)
    nc.set_auto_maskandscale(False)
    var_name, slices = encoder._interpret_var_spec(var_spec)
    section = encoder._interpret_slices(slices, nc.variables[var_name].get_dims())

    assert type(ds) == xr.Dataset  # ensure that dataset is correct
    assert (ds.variables[var_name][:].data == nc.variables[var_name][encoder.interpret_section(section)]).all()  # check if data matches
