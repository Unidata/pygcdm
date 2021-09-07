"""Class to decode a gRPC message into a netCDF file."""

import numpy as np
import xarray as xr
from src.netcdf_grpc import gRPC_netCDF


class netCDF_Decode(gRPC_netCDF):
    """Decode gRPC message into netCDF file."""

    def __init__(self):
        """Initialize decoder class.

        Inherits type conversion utilities, common error handling,
        and other common encoder/decoder utility functions.

        Also initializes an empty xarray dataset object to "pack"
        with information.
        """
        super().__init__()
        self.ds = xr.Dataset()

    # high level decode stuff
    def generate_file_from_response(self, header, data, as_netcdf=False):
        """Interpret response messages and process responses into xarray
        dataset object.
        """

        # unpack header
        self._handle_error(header.error)
        header_error = header.error  # bone add in error handling
        header_version = header.version

        # unpack data
        self._handle_error(data.error)
        data_error = data.error  # bone add in error handling
        data_version = data.version
        data_location = data.location
        var_name = data.variable_spec.split('(')[0]
        data_variable_full_name = data.var_full_name.strip('/')  # BONE how to handle this

        # create a list of slices from data section and header shapes by associating based on common variable name
        for var in header.header.root.vars:
            if var.name == var_name:
                var_dims = [shape.name for shape in var.shapes]
        slice_dict = dict(zip(var_dims, self.interpret_section(data.section)))

        # decode data
        self._decode_response(header.header.root, var_name, data.data, slice_dict)

        # return file based on user input
        if as_netcdf:
            return self.ds.to_netcdf()
        else:
            return self.ds

    def _handle_error(self, error):
        # bone implement this
        pass

    def _decode_response(self, group, var_name, data, slice_dict):
        """Function to assign dimensions and update attributes"""
    
        # start with updating attributes
        # coordinates are stored as variables so we process them when iterating through vars
        self.ds.attrs.update({attr.name: self._decode_data(attr.data) for attr in group.atts})

        # next unpack data
        for var in group.vars:
            # `var` is the list of variables stored in the HeaderResponse message
            # `data` is the actual (non-coordinate) data contained in the `DataResponse` message

            # first handle coordinates
            if var.name in slice_dict:
                coord_data = self._decode_data(var.data)
                coord_data = [coord_data] if isinstance(coord_data, int) else list(coord_data)
                if var.name in self.ds.dims:
                    self.ds = self.ds.assign_coords({var.name: coord_data[slice_dict[var.name]]})
                else:
                    self.ds = self.ds.expand_dims(dim={var.name: coord_data[slice_dict[var.name]]})

            # next handle named variable that is not coordinate
            if var.name == var_name:
                self.ds[var.name] = xr.DataArray(
                        dims=[dim.name for dim in var.shapes],
                        attrs={attr.name: self._decode_data(attr.data) for attr in var.atts},
                        data=np.array(self._decode_data(data)).reshape(data.shapes),
                        )

    def _decode_data(self, data):
        dtype = self.get_message_data_type(data.data_type)
        if dtype == 'sdata':
            # want string data as contiguous string not list
            return ''.join(getattr(data, dtype))
        else:
            # since field is repeated, will always return a list even if one element. This returns a scalar where appropriate
            return getattr(data, dtype) if len(getattr(data, dtype)) > 1 else getattr(data, dtype)[0]
