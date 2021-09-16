"""Class to encode netCDF file into a gRPC message."""

import netCDF4 as nc4
from pygcdm.protogen import gcdm_netcdf_pb2 as grpc_msg
from pygcdm.netcdf_grpc import gRPC_netCDF
import numpy as np
import re
import math
import os

class netCDF_Encode(gRPC_netCDF):
    """Encode netCDF file into gRPC message type defined in `protos` folder."""

    def __init__(self):
        """Initialize encoder class.

        Inherits type conversion utilities, common error handling,
        and other common encoder/decoder utility functions.
        """
        super().__init__()
        self.error = self._generate_error()

    def generate_header_from_request(self, request):
        """Method to take `HeaderRequest` message types and return a `HeaderResponse` message."""
        # check request type
        try:
            assert isinstance(request, grpc_msg.HeaderRequest)
        except AssertionError:
            return grpc_msg.HeaderResponse(error=self._generate_error("bad_request_header"))

        # check request location
        try:
            assert os.path.isfile(request.location)
        except AssertionError:
            return grpc_msg.HeaderResponse(error=self._generate_error("bad_path"))

        # check filetype is nc
        try:
            nc = nc4.Dataset(request.location)
        except (FileNotFoundError, OSError):
            return grpc_msg.HeaderResponse(error=self._generate_error("bad_file"))

        # finally generate header if error checks pass
        header_response_args = {}
        header_args = {}
        nc.set_auto_maskandscale(False)
        header_args['title'] = nc.getncattr('title') if 'title' in nc.ncattrs() else None
        header_args['id'] = nc.getncattr('id') if 'id' in nc.ncattrs() else None
        header_response_args['header'] = grpc_msg.Header(location=request.location,
                                                         root=self._encode_group(nc),
                                                         **header_args
                                                         )
        header_response_args['error'] = self._generate_error(None)
        return grpc_msg.HeaderResponse(**header_response_args)

    def generate_data_from_request(self, request):
        """Method to take `DataRequest` message types and return a `DataResponse` message."""
        # check request type
        try:
            assert isinstance(request, grpc_msg.DataRequest)
        except AssertionError:
            return grpc_msg.DataResponse(error=self._generate_error("bad_request_data"))

        # check request location
        try:
            assert os.path.isfile(request.location)
        except AssertionError:
            return grpc_msg.DataResponse(error=self._generate_error("bad_path"))

        # check filetype is nc
        try:
            nc = nc4.Dataset(request.location)
            nc.set_auto_maskandscale(False)
        except (FileNotFoundError, OSError):
            return grpc_msg.HeaderResponse(error=self._generate_error("bad_file"))

        # check variable spec: first check if works, next check specific failure mechanisms
        try:
            var_name, var_spec_slices = self._interpret_var_spec(request.variable_spec)
            try:  # check for proper variable name
                assert var_name in nc.variables
            except AssertionError:
                return grpc_msg.HeaderResponse(error=self._generate_error("bad_varspec_variable"))
            try:  # check for proper number of dimensions
                if var_spec_slices is not None and len(var_spec_slices) != 0:
                    assert len(var_spec_slices) == len(nc.variables[var_name].dimensions)
            except AssertionError:
                return grpc_msg.HeaderResponse(error=self._generate_error("bad_varspec_variable_dim_mismatch"))
            try:  # check for slices don't exceed maximum variable dimension
                section = self._interpret_slices(var_spec_slices, nc.variables[var_name].get_dims())
                for rng, shape in zip(section.ranges, nc.variables[var_name].shape):
                    assert shape >= rng.start + rng.size*rng.stride
            except AssertionError:
                return grpc_msg.HeaderResponse(error=self._generate_error("bad_varspec_variable_dim_exceed"))
        except Exception as err:  
            print(err)
            return grpc_msg.HeaderResponse(error=self._generate_error("bad_varspec"))

        section = self._interpret_slices(var_spec_slices, nc.variables[var_name].get_dims())
        slices = self.interpret_section(section)
        variable = nc.variables[var_name][(*slices,)]
        data_type = self.get_grpc_type(variable.dtype.type)
        data = self._encode_data(variable, data_type)

        return grpc_msg.DataResponse(error=self._generate_error(None),
                                     version=self.get_version(),
                                     location=request.location,
                                     variable_spec=request.variable_spec,
                                     var_full_name=nc.variables[var_name].group().name + nc.variables[var_name].name,
                                     section=section,
                                     data=data
                                     )

    def _interpret_var_spec(self, var_spec):
        var_name, *var_spec_slices = re.split(r'\(|\)|,', var_spec)
        var_spec_slices = var_spec_slices[:-1] if len(var_spec_slices) > 0 else None
        return var_name, var_spec_slices

    def _interpret_slices(self, var_spec_slices, var_dims):
        # using definition from:
        # https://docs.unidata.ucar.edu/netcdf-java/7.0/javadoc/ucar/nc2/ParsedArraySectionSpec.html

        if var_spec_slices is None:
            section = grpc_msg.Section(ranges=[grpc_msg.Range(size=dim.size, stride=1) for dim in var_dims])
        else:
            ranges = []
            for slice_idx, var_slice in enumerate(var_spec_slices):
                # handle : condition
                if var_slice.strip() == ':':
                    ranges.append(grpc_msg.Range(size=var_dims[slice_idx].size, stride=1))
                # handle  single index condition
                elif str.isdigit(var_slice):
                    if int(var_slice) == 0:
                        ranges.append(grpc_msg.Range(size=1, stride=1))
                    else:
                        ranges.append(grpc_msg.Range(start=int(var_slice), size=1, stride=1))
                # else, unpack the range
                else:
                    range_attr = ['start', 'size', 'stride']
                    rng = grpc_msg.Range()
                    start, end, *stride = [int(i) for i in var_slice.split(':')]
                    if len(stride):  # max one item in list
                        stride = stride.pop()
                    else:
                        stride = 1
                    range_vals = [start, math.ceil((end-start+1)/stride), stride]
                    for attr, val in zip(range_attr, range_vals):
                        setattr(rng, attr, int(val))
                    ranges.append(rng)
            section = grpc_msg.Section(ranges=ranges)
        return section

    def _get_attribute_type(self, attribute):
        if np.isscalar(attribute):
            if issubclass(type(attribute), np.number):
                data_type = attribute.dtype.type
            else:
                data_type = type(attribute)
        else:
            if isinstance(attribute, np.ndarray):
                data_type = attribute.dtype.type
            else:
                data_type = type(attribute[0])

        return self.get_grpc_type(data_type)

    # GROUP STUFF
    def _encode_group(self, group):
        # TODO: add support for structures, enum_types. Verify subgroup encoding works
        dims = self._encode_dimension(group)
        dim_names = [dim.name for dim in dims]
        variables = [
                self._encode_variable(variable) if variable.name in dim_names
                else self._encode_variable(variable, coords_only=True)
                for variable in group.variables.values()
                ]
        atts = self._encode_attributes(group)
        groups = [self._encode_group(subgroup) for subgroup in group.groups.values()]
        return grpc_msg.Group(name=group.name,
                              dims=dims,
                              vars=variables,
                              atts=atts,
                              groups=groups
                              )

    def _encode_variable(self, variable, coords_only=False):
        shapes = self._encode_dimension(variable)
        atts = self._encode_attributes(variable)
        data_type = self.get_grpc_type(variable.dtype.type)
        data = self._encode_data(variable, data_type) if not coords_only else grpc_msg.Data()
        return grpc_msg.Variable(name=variable.name,
                                 data_type=data_type,
                                 shapes=shapes,
                                 atts=atts,
                                 data=data
                                 )

    def _encode_attributes(self, obj):
        attributes = []
        for attribute_name in obj.ncattrs():
            attribute = obj.getncattr(attribute_name)
            data_type = self._get_attribute_type(attribute)
            data = self._encode_data(attribute, data_type)
            if isinstance(attribute, str):
                length = 0
            else:
                if np.isscalar(attribute):
                    length = 0
                else:
                    length = len(attribute)
            attributes.append(grpc_msg.Attribute(
                name=attribute_name,
                data_type=data_type,
                length=length,
                data=data,
                ))
        return attributes

    def _encode_data(self, obj, data_type):
        # strings are inherently iterable so we leave them as is
        # else we convert to numpy array since this is easier to deal with than both lists and arrays
        if np.isscalar(obj):
            if isinstance(obj, str):
                data = obj
                shapes = [len(obj)]
            else:
                data = [obj]
                shapes = 0

        else:
            data = np.asarray(obj).flatten().tolist()
            shapes = np.asarray(obj).shape

        # find data type to pack message, error if data_type not found in dict
        dtype = self.get_message_data_type(data_type)
        dmsg = grpc_msg.Data(data_type=data_type, shapes=shapes)
        getattr(dmsg, dtype).extend(data)  # get attr returns and iter object which we can then extend code onto
        return dmsg

    def _encode_dimension(self, obj):
        # groups store dimensions in dict, variables store dimensions in tuple
        # handle group condition:
        if isinstance(obj.dimensions, dict):
            group_dims = []
            for dimension in obj.dimensions.values():
                group_dims.append(grpc_msg.Dimension(
                    name=dimension.name,
                    length=dimension.size,
                    is_unlimited=dimension.isunlimited(),
                    ))
            return group_dims

        # handle variable condition
        elif isinstance(obj.dimensions, tuple):
            return [grpc_msg.Dimension(name=name, length=length) for name, length in zip(obj.dimensions, obj.shape)]

        # handle error condition
        else:
            raise NotImplementedError('Dimension encoding is only supported for groups and variables')
