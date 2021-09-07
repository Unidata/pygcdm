"""Class to encode netCDF file into a gRPC message."""

import netCDF4 as nc4
from src.protogen import gcdm_netcdf_pb2 as grpc_msg
from src.netcdf_grpc import gRPC_netCDF
import numpy as np
import re
import math


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
        nc = nc4.Dataset(request.location)
        nc.set_auto_maskandscale(False)
        error = self._generate_error()  # BONE need to figure out error handling
        # BONE need to include title, id in header
        header = grpc_msg.Header(location=request.location,
                                 root=self._encode_group(nc)
                                 )
        return grpc_msg.HeaderResponse(error=error,
                                       version=self.get_version(),
                                       header=header
                                       )

    def generate_data_from_request(self, request):
        """Method to take `DataRequest` message types and return a `DataResponse` message."""
        nc = nc4.Dataset(request.location)
        nc.set_auto_maskandscale(False)
        error = self._generate_error()  # need to figure out error handling
        var_name, section = self._interpret_spec(request.variable_spec, nc)
        slices = self.interpret_section(section)
        variable = nc.variables[var_name][(*slices,)]
        data_type = self.get_grpc_type(variable.dtype.type)
        data = self._encode_data(variable, data_type)

        return grpc_msg.DataResponse(error=error,
                                     version=self.get_version(),
                                     location=request.location,
                                     variable_spec=request.variable_spec,
                                     var_full_name=nc.variables[var_name].group().name + nc.variables[var_name].name,
                                     section=section,
                                     data=data
                                     )

    def _interpret_spec(self, var_spec, nc):
        # using definition from:
        # https://docs.unidata.ucar.edu/netcdf-java/7.0/javadoc/ucar/nc2/ParsedArraySectionSpec.html

        if '(' in var_spec:
            var_name, dims, _ = re.split('\(|\)', var_spec)
            ranges = []
            for dim_idx, dim in enumerate(dims.split(',')):
                # handle : condition
                if dim == ':':
                    ranges.append(grpc_msg.Range(size=nc.variables[var_name].get_dims()[dim_idx].size, stride=1))
                # handle  single index condition
                elif str.isdigit(dim):
                    if int(dim) == 0:
                        ranges.append(grpc_msg.Range(size=1, stride=1))
                    else:
                        ranges.append(grpc_msg.Range(start=int(dim), size=1, stride=1))
                # else, unpack the range
                else:
                    range_attr = ['start', 'size', 'stride']
                    rng = grpc_msg.Range()
                    start, end, *stride = [int(i) for i in dim.split(':')]
                    if len(stride):  # max one item in list
                        stride = stride.pop()
                    else:
                        stride = 1
                    range_vals = [start, math.ceil((end-start+1)/stride), stride]
                    for attr, val in zip(range_attr, range_vals):
                        setattr(rng, attr, int(val))
                    ranges.append(rng)

            # bone, this is a good opportunity for error code of invalid dimensions
            section = grpc_msg.Section(ranges=ranges)
        else:
            var_name = var_spec
            section = grpc_msg.Section(ranges=[grpc_msg.Range(size=dim.size, stride=1) for dim in nc.variables[var_name].get_dims()])

        return var_name, section

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
