"""Class to decode a gRPC message into a netCDF file."""

import numpy as np
import xarray as xr
from pygcdm.netcdf_grpc import gRPC_netCDF


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

    # high level decode stuff
    def generate_file_from_response(self, header, data=None, as_netcdf=False):
        """Interpret response messages and process responses into xarray dataset object.

        `header` = `HeaderResponse` message to decode
        `data` (optional) = `DataResponse` message to decode.
        `as_netcdf` (optional) = Boolean, determines if file should be decoded as
            `xarray.DataSet` object or `netCDF4.Dataset` object.
        """
        # initialize ds object
        ds = xr.Dataset()

        # unpack header
        header_error = header.error  
        if header.error.message != self._generate_error(None).message:
            ds.attrs = {"error code": header.error.code, "error message":header.error.message}
            return ds

        header_version = header.version
        ds = self._decode_header_response(ds, header.header.root)

        # unpack data

        if data is not None:
            if data.error.message != self._generate_error(None).message:
                ds.attrs = {"error code": data.error.code, "error message":data.error.message}
                return ds
            data_error = data.error
            data_version = data.version
            data_location = data.location
            var_name = data.variable_spec.split('(')[0]
            data_variable_full_name = data.var_full_name.strip('/')  # TODO: make consistent with netcdf-java 

            # create a list of slices from data section and header shapes by associating based on common variable name
            for var in header.header.root.vars:
                if var.name == var_name:
                    var_dims = [shape.name for shape in var.shapes]
            slice_dict = dict(zip(var_dims, self.interpret_section(data.section)))

            # decode data
            ds = self._decode_data_response(ds, header.header.root, var_name, data.data, slice_dict)

        # return file based on user input
        if as_netcdf:
            return ds.to_netcdf()
        else:
            return ds

    def _decode_header_response(self, ds, group):
        """Function to decode information in header response."""
        # start with updating attributes
        # coordinates are stored as variables so we process them when iterating through vars
        ds.attrs.update({attr.name: self._decode_data(attr.data) for attr in group.atts})
        for var in group.vars:
            # `var` is the list of variables stored in the HeaderResponse message
            # `data` is the actual (non-coordinate) data contained in the `DataResponse` message

            # first handle coordinates
            if var.name in [dim.name for dim in group.dims]:
                coord_data = self._decode_data(var.data)
                coord_data = [coord_data] if isinstance(coord_data, int) else list(coord_data)
                if var.name in ds.dims:
                    ds = ds.assign_coords({var.name: coord_data})
                else:
                    ds = ds.expand_dims(dim={var.name: coord_data})

            # next handle named variable that is not coordinate
            # this writes in variable attributes with variable values as `nan`
            else:
                ds[var.name] = xr.DataArray(
                    attrs={attr.name: self._decode_data(attr.data) for attr in var.atts},
                    )
        return ds

    def _decode_data_response(self, ds, group, var_name, data, slice_dict):
        """Function to assign dimensions and update attributes."""
        # next unpack data
        for var in group.vars:
            # `var` is the list of variables stored in the HeaderResponse message
            # `data` is the actual (non-coordinate) data contained in the `DataResponse` message

            # first handle coordinates
            if var.name in slice_dict:
                coord_data = self._decode_data(var.data)
                coord_data = [coord_data] if isinstance(coord_data, int) else list(coord_data)
                if var.name in ds.dims:
                    ds = ds.assign_coords({var.name: coord_data[slice_dict[var.name]]})
                else:
                    ds = ds.expand_dims(dim={var.name: coord_data[slice_dict[var.name]]})

            # next handle named variable that is not coordinate
            elif var.name == var_name:
                ds[var.name] = xr.DataArray(
                    dims=[dim.name for dim in var.shapes],
                    attrs={attr.name: self._decode_data(attr.data) for attr in var.atts},
                    data=np.array(self._decode_data(data)).reshape(data.shapes),
                    )

            # _decode_header_response writes in dummy `nan` data so we remove if we're expecting data
            else:
                ds = ds.drop_vars(var.name)

        return ds

    def _decode_data(self, data):
        dtype = self.get_message_data_type(data.data_type)
        if dtype == 'sdata':
            # want string data as contiguous string not list
            return ''.join(getattr(data, dtype))
        else:
            # since field is repeated, will always return a list even if one element. This returns a scalar where appropriate
            return getattr(data, dtype) if len(getattr(data, dtype)) > 1 else getattr(data, dtype)[0]
