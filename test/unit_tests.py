import pytest
from pygcdm.netcdf_encode import *
import pygcdm.protogen.gcdm_netcdf_pb2 as msg
import netCDF4 as nc4
import os

def test_interpret_spec():
    nc = nc4.Dataset('test/data/test3.nc')
    encoder = netCDF_Encode()

    # test variable name, no slices
    var_spec = 'analysed_sst'
    var_name, slices = encoder._interpret_var_spec(var_spec)
    section = encoder._interpret_slices(slices, [*nc.dimensions.values()])
    sizes = [1, 720, 1440]
    strides = [1, 1, 1]
    assert section == msg.Section(ranges=[msg.Range(size=s, stride=st) for s,st in zip(sizes, strides)])

    # test variable name, ellipses
    var_spec = 'analysed_sst(:,:,:)'
    var_name, slices = encoder._interpret_var_spec(var_spec)
    section = encoder._interpret_slices(slices, [*nc.dimensions.values()])
    sizes = [1, 720, 1440]
    strides = [1, 1, 1]
    assert section == msg.Section(ranges=[msg.Range(size=s, stride=st) for s,st in zip(sizes, strides)])

    # test variable name, ellipses w/ space
    var_spec = 'analysed_sst(:, :, :)'
    var_name, slices = encoder._interpret_var_spec(var_spec)
    section = encoder._interpret_slices(slices, [*nc.dimensions.values()])
    sizes = [1, 720, 1440]
    strides = [1, 1, 1]
    assert section == msg.Section(ranges=[msg.Range(size=s, stride=st) for s,st in zip(sizes, strides)])

    # test variable name, slices
    var_spec = 'analysed_sst(0, 0:719:10, 0:1439:10)'
    var_name, slices = encoder._interpret_var_spec(var_spec)
    section = encoder._interpret_slices(slices, [*nc.dimensions.values()])
    sizes = [1, 72, 144]
    strides = [1, 10, 10]
    assert section == msg.Section(ranges=[msg.Range(size=s, stride=st) for s,st in zip(sizes, strides)])

    # test variable name, slices, starts
    var_spec = 'analysed_sst(0, 200:700:10, 1300:1400:10)'
    var_name, slices = encoder._interpret_var_spec(var_spec)
    section = encoder._interpret_slices(slices, [*nc.dimensions.values()])
    sizes = [1, 51, 11]
    strides = [1, 10, 10]
    starts = [None, 200, 1300]
    assert section == msg.Section(ranges=[msg.Range(size=s, stride=st, start=sa) for s,st,sa in zip(sizes, strides, starts)])
