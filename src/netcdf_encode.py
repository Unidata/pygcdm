import gen.gcdm_netcdf_pb2 as grpc_msg
import netCDF4 as nc4
import numpy as np
import xarray as xr
import re

class gRPC_netCDF():
    def __init__(self):
        self.typeDict = self.GenTypeDict()
    
    def GenTypeDict(self):
        # BONE work in progress
        return {
                # native python types
                int:grpc_msg.DATA_TYPE_INT,
                str:grpc_msg.DATA_TYPE_STRING,
                float:grpc_msg.DATA_TYPE_FLOAT,

                np.int8:grpc_msg.DATA_TYPE_BYTE,
                np.int16:grpc_msg.DATA_TYPE_SHORT,
                np.int32:grpc_msg.DATA_TYPE_INT,
                np.int64:grpc_msg.DATA_TYPE_LONG,

                np.float16:grpc_msg.DATA_TYPE_FLOAT,
                np.float32:grpc_msg.DATA_TYPE_FLOAT,
                np.float64:grpc_msg.DATA_TYPE_FLOAT,

                np.byte:grpc_msg.DATA_TYPE_BYTE,
                np.ubyte:grpc_msg.DATA_TYPE_UBYTE,
                np.short:grpc_msg.DATA_TYPE_SHORT,
                np.ushort:grpc_msg.DATA_TYPE_USHORT,
                np.double:grpc_msg.DATA_TYPE_DOUBLE,

                np.uint8:grpc_msg.DATA_TYPE_UBYTE,
                np.uint16:grpc_msg.DATA_TYPE_USHORT,
                np.uint32:grpc_msg.DATA_TYPE_UINT,
                np.uint64:grpc_msg.DATA_TYPE_ULONG,
                np.uint:grpc_msg.DATA_TYPE_ULONG,
                }
    
    def GetGRPCType(self, data_type):
        try:
            return self.typeDict(data_type)
        except:
            raise NotImplementedError("Type not supported")

    def GenerateError(self):
        # BONE idea:
        # 1. check for errors with java implementation
        # 2. this should probably broken out into a grpc parent class
        # 3. have errors reflect what you punted on
        message = "Dummy error" # bone
        code = 0
        return grpc_msg.Error(message=message, code=code)

class netCDF_Encode(gRPC_netCDF):

    def __init__(self):
        super().__init__()

    ## HIGH LEVEL REQUEST STUFF

    def GenerateHeaderFromRequest(self, request):
        nc = nc4.Dataset(request.location)
        error = self.GenerateError()  # BONE this is dummy, need to figure out error handling
        version = 1 # BONE, this is dummy
        header = grpc_msg.Header(location=self.headerRequest.location,
                root = self.EncodeGroup(nc)
                )
        return grpc_msg.HeaderResponse(error=error,
                version=version,
                header=header)

    def GenerateDataFromRequest(self, request):
        nc = nc4.Dataset(request.location)
        error = self.GenerateError()  # BONE this is dummy, need to figure out error handling
        version = 1 # BONE, this is dummy
        location = request.location
        variable_spec = request.variable_spec
        variable, section = self.InterpretSpec(request.variable_spec, nc)
        var_full_name = nc.variables[variable]
        data = self.EncodeVariableData(nc, variable, section)

    def InterpretSpec(self, var_spec, nc):
        # using definition from: 
        # https://docs.unidata.ucar.edu/netcdf-java/7.0/javadoc/ucar/nc2/ParsedArraySectionSpec.html

        ncdim_sizes = [dim.size for dim in nc.dimensions.values()]
        
        if "(" in var_spec:
            varName, dims, _ = re.split("\(|\)", var_spec)
            section = []
            for ncdim_idx, dim in enumerate(dims.split(",")):
                if dim == ":":
                    section.append(grpc_msg.Range(size=ncdim_sizes[ncdim_idx], stride=1)
                elif str.isdigit(dim):
                    if int(dim) == 0:
                        section.append(grpc_msg.Range(size=1, stride=1)
                    else
                        section.append(grpc_msg.Range(start=int(dim), size=1, stride=1)
                else:
                    range_attr = ["start", "end", "stride"]
                    rng = grpc_msg.Range()
                    for attr, val in zip(range_attr, dim):
                        setattr(rng, attr, int(val))
                    section.append(rng)
            
            # bone, this is a good opportunity for error code of invalid dimensions
        else:
            varName = var_spec
            section = grpc_msg.Section()  # empty

        return varName, section

    ## GROUP STUFF
    def EncodeGroup(self, group):
        name = group.name
        dims = self.EncodeDimension(group)
        variables = self.EncodeGroupVariables(group)
        # BONE need to add support for structures
        atts = self.EncodeAttributes(group)
        groups = [self.EncodeGroup(subgroup) for subgroup in group.groups.values()]
        # BONE need to add support for enum_types
        return grpc_msg.Group(name=name,
                dims=dims,
                vars=variables,
                atts=atts,
                groups=groups
                )


    ## VARIABLE STUFF
    def EncodeGroupVariables(self, group):
        return [self.EncodeVariable(variable) for variable in group.variables]

    def EncodeVariable(self, variable):
        name = variable.name
        data_type = self.GetGRPCType(variable.dtype)
        shapes = self.EncodeDimension(variable)
    
    ## ATTRIBUTE STUFF
    def EncodeAttributes(self, obj):
        attributes = []
        for attribute_name in obj.ncattrs():
            attribute = obj.getncattr(attribute_name)
            data_type = self.GetGRPCType(type(attribute))
            if isinstance(attribute, list):
                length = len(attribute)
            else:
                length = 0
            data = self.EncodeAttributeData(attribute, length)
            attributes.append(grpc_msg.Attribute(name=attribute_name,
                data_type=data_type,
                length=length,
                data=data)
        return attributes

    ## DATA STUFF
    def EncodeAttributeData(self, attribute, length):
        data_type = self.GetGRPCType(type(attribute))
        shapes = length
        return self.EncodeData(data_type, shapes, attribute)

    def EncodeVariableData(self, nc, variable, section):
        data_type = self.GetGRPCType(nc.variables[variable].dtype)
        shapes = list(nc.variables[variable].shape)
        data = nc.variables[variable].data.flatten().tolist()
        return self.EncodeData(data_type, shapes, data)

    def EncodeData(self, data_type, shapes, data):
        if isinstance(data_type, (grpc_msg.DATA_TYPE_BYTE)):
            return grpc_msg.Data(data_type=data_type, shapes=shapes, bdata=data)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_SHORT, grpc_msg.DATA_TYPE_INT)):
            return grpc_msg.Data(data_type=data_type, shapes=shapes, idata=data)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_USHORT, grpc_msg.DATA_TYPE_UINT)):
            return grpc_msg.Data(data_type=data_type, shapes=shapes, uidata=data)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_LONG)):
            return grpc_msg.Data(data_type=data_type, shapes=shapes, ldata=data)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_ULONG)):
            return grpc_msg.Data(data_type=data_type, shapes=shapes, uldata=data)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_FLOAT)):
            return grpc_msg.Data(data_type=data_type, shapes=shapes, fdata=data)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_DOUBLE)):
            return grpc_msg.Data(data_type=data_type, shapes=shapes, ddata=data)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_STRING)):
            return grpc_msg.Data(data_type=data_type, shapes=shapes, sdata=data)
        else:
            raise NotImplementedError("Data type not supported")

    ## DIMENSIONS STUFF
    def EncodeDimension(self, obj):
        # first determine if dimension object is a group or a variable
        # groups store dimensions in dict, variables store dimensions in tuple
        if isinstance(obj.dimensions, dict):
            return self.EncodeDimensionGroup(obj)
        elif isinstance(obj.dimensions, tuple):
            return self.EncodeDimensionVariable(obj)
        else:
            raise NotImplementedError("Dimension encoding is only supported for groups and variables")

    def EncodeDimensionsGroup(self, group):
        dimension_list = []
        for dimension in group.dimensions.values():
            dimension_list.append(grpc_msg.Dimension(
                name=dimension.name,
                length=dimension.size,
                is_unlimited=dimension.isunlimited(),
                ))
        return dimension_list

    def EncodeDimensionsVariable(self, variable):
        return [grpc_msg.Dimension(name=name, length=length) for name, length in zip(variable.dimensions, variable.shape)]
    
class netCDF_Decode(gRPC_netCDF):

    def __init__(self):
        super().__init__()

    # high level decode stuff
    def GenerateFileFromResponse(self, header, data):
        
        # create new, empty file
        self.ds = xr.Dataset()

        # unpack header
        headerError = header.error  # bone add in error handling
        headerVersion = header.version
        self.DecodeHeaderResponse(header.header)
        
        # unpack data
        dataError = data.error  # bone add in error handling
        dataVersion = data.version
        dataLocation = data.location
        dataVariableSpec = data.variable_spec
        dataVariableFullName = data.var_full_name
        self.DecodeDataResponse(dataVariableFullName, data.section, data.data)

        return self.ds

    def DecodeHeaderResponse(self, header):
        group = header.root
        self.ds.expand_dims({dim.name:dim.value for dim in group.dims})
        for var in group.vars:
            da = xr.DataArray()
            da.expand_dims({dim.name:dim.value for dim in var.shapes})
            da.attrs.update({attr.name:self.DecodeData(attr.data) for attr in var.atts})
            self.ds.update({var.name:da})

    def DecodeDataResponse(self, varName, section, data):
        slices = [slice(rng.start, rng.start+rng.stop, rng.stride) for rng in section]
        pack_array = np.empty([v for v in dict(self.ds.dims).values()])
        raw_data = np.array(self.DecodeData(data)).reshape(data.shapes)
        self.ds.variables[varName].values = pack_array[tuple(slices)]

    def DecodeData(self, data):
        if isinstance(data.data_type, (grpc_msg.DATA_TYPE_BYTE)):
            return [d for d in data.bdata]
        elif isinstance(data.data_type, (grpc_msg.DATA_TYPE_SHORT, grpc_msg.DATA_TYPE_INT)):
            return [d for d in data.idata]
        elif isinstance(data.data_type, (grpc_msg.DATA_TYPE_USHORT, grpc_msg.DATA_TYPE_UINT)):
            return [d for d in data.uidata]
        elif isinstance(data.data_type, (grpc_msg.DATA_TYPE_LONG)):
            return [d for d in data.ldata]
        elif isinstance(data.data_type, (grpc_msg.DATA_TYPE_ULONG)):
            return [d for d in data.uldata]
        elif isinstance(data.data_type, (grpc_msg.DATA_TYPE_FLOAT)):
            return [d for d in data.fdata]
        elif isinstance(data.data_type, (grpc_msg.DATA_TYPE_DOUBLE)):
            return [d for d in data.ddata]
        elif isinstance(data.data_type, (grpc_msg.DATA_TYPE_STRING)):
            return [d for d in data.sdata]
        else:
            raise NotImplementedError("Data type not supported")

#    def DecodeData(self, section, data):
#        ???



if __name__=="__main__":
    hr = grpc_msg.HeaderRequest(location="test2.nc")
    header = gRPC_Header(hr)
