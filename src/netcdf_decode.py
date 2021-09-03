import numpy as np
import xarray as xr
from src.netcdf_grpc import gRPC_netCDF

class netCDF_Decode(gRPC_netCDF):

    def __init__(self):
        super().__init__()
        self.ds = xr.Dataset()

    # high level decode stuff
    def GenerateFileFromResponse(self, header, data, as_netcdf=False):

        # unpack header
        headerError = header.error  # bone add in error handling
        headerVersion = header.version
        
        # unpack data
        dataError = data.error  # bone add in error handling
        dataVersion = data.version
        dataLocation = data.location
        var_name = data.variable_spec.split("(")[0]
        dataVariableFullName = data.var_full_name.strip("/")  # BONE how to handle this

        # create a list of slices from data section and header shapes by associating based on common variable name
        for var in header.header.root.vars:
            if var.name == var_name:
                var_dims = [shape.name for shape in var.shapes]
        slice_dict = dict(zip(var_dims, self.InterpretSection(data.section)))

        # decode data
        self.DecodeResponse(header.header.root, var_name, data.data, slice_dict)

        # return file based on user input
        if as_netcdf:
            return self.ds.to_netcdf()
        else:
            return self.ds

    def DecodeResponse(self, group, var_name, data, slice_dict):
        # assign dimensions, update attributes
        # coordinates are stored as variables so we process them when iterating through vars
        self.ds.attrs.update({attr.name:self.DecodeData(attr.data) for attr in group.atts})  # this returns list of data
        for var in group.vars:
            # first handle coordinates
            if var.name in slice_dict:
                coord_data = self.DecodeData(var.data)
                coord_data = [coord_data] if isinstance(coord_data, int) else list(coord_data)
                if var.name in self.ds.dims:
                    self.ds = self.ds.assign_coords({var.name:coord_data[slice_dict[var.name]]})
                else:
                    self.ds = self.ds.expand_dims(dim={var.name:coord_data[slice_dict[var.name]]})

            if var.name == var_name:
                self.ds[var.name] = xr.DataArray(
                        dims = [dim.name for dim in var.shapes],
                        attrs = {attr.name:self.DecodeData(attr.data) for attr in var.atts},
                        data = np.array(self.DecodeData(data)).reshape(data.shapes),  # BONE, data comes from the data, var.data comes from header. This is confusing and variables should probably be reworded
                        )

    def DecodeData(self, data):
        dtype = self.GetMessageDataType(data.data_type)
        if dtype == "sdata":
            # want string data as contiguous string not list
            return "".join(getattr(data, dtype))  
        else:
            # since field is repeated, will always return a list even if one element. This returns a scalar where appropriate
            return getattr(data, dtype) if len(getattr(data, dtype)) > 1 else getattr(data, dtype)[0]
