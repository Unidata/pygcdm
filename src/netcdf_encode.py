import gen.gcdm_netcdf_pb2 as grpc_msg
import netCDF4 as nc4
import numpy as np
import xarray as xr
import re
import math

class gRPC_netCDF():
    def __init__(self):
        self.typeDict = self.GenTypeDict()
        self.messageDict = self.GenMessageTypeDict()
    
    def GenTypeDict(self):
        # BONE work in progress
        return {
                # native python types
                int:grpc_msg.DATA_TYPE_INT,
                str:grpc_msg.DATA_TYPE_STRING,
                float:grpc_msg.DATA_TYPE_FLOAT,

                np.int8:grpc_msg.DATA_TYPE_INT,
                np.int16:grpc_msg.DATA_TYPE_INT,
                np.int32:grpc_msg.DATA_TYPE_INT,
                np.int64:grpc_msg.DATA_TYPE_LONG,

                np.float16:grpc_msg.DATA_TYPE_FLOAT,
                np.float32:grpc_msg.DATA_TYPE_FLOAT,
                np.float64:grpc_msg.DATA_TYPE_FLOAT,

                np.byte:grpc_msg.DATA_TYPE_INT,  # np.byte defaults to np.int8 which causes trouble
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

    def GenMessageTypeDict(self):
        return  {
                grpc_msg.DATA_TYPE_BYTE:"bdata",
                grpc_msg.DATA_TYPE_SHORT:"idata",
                grpc_msg.DATA_TYPE_INT:"idata",
                grpc_msg.DATA_TYPE_USHORT:"uidata",
                grpc_msg.DATA_TYPE_UINT:"uidata",
                grpc_msg.DATA_TYPE_LONG:"ldata",
                grpc_msg.DATA_TYPE_ULONG:"uldata",
                grpc_msg.DATA_TYPE_FLOAT:"fdata",
                grpc_msg.DATA_TYPE_DOUBLE:"ddata",
                grpc_msg.DATA_TYPE_STRING:"sdata",
                }
    
    def GetGRPCType(self, data_type):
        try:
            return self.typeDict[data_type]
        except:
            raise NotImplementedError("Type not supported")

    def GetMessageDataType(self, data_type):
        # find data type to pack message, error if data_type not found in dict
        try:
            return self.messageDict[data_type]
        except:
            raise NotImplementedError("Incorrect message data type")

    def GenerateError(self):
        # BONE idea:
        # 1. check for errors with java implementation
        # 2. have errors reflect what you punted on
        message = "Dummy error" # bone
        code = 0
        return grpc_msg.Error(message=message, code=code)

    def InterpretSection(self, section):
        slices = []
        for rng in section.ranges:
            if rng.size == 1:
                slices.append(slice(rng.start, rng.start+1))
            else:
                # empty fields default to zero; numpy can't do zero step indexing
                if rng.stride == 0:
                    slices.append(slice(rng.start, rng.start+rng.stride*rng.size, 1))
                else:
                    slices.append(slice(rng.start, rng.start+rng.stride*rng.size, rng.stride))
        return slices

    def InterpretSpec(self, var_spec, ncdim_sizes):
        # using definition from: 
        # https://docs.unidata.ucar.edu/netcdf-java/7.0/javadoc/ucar/nc2/ParsedArraySectionSpec.html

        
        if "(" in var_spec:
            varName, dims, _ = re.split("\(|\)", var_spec)
            ranges = []
            for ncdim_idx, dim in enumerate(dims.split(",")):
                # handle : condition
                if dim == ":":
                    ranges.append(grpc_msg.Range(size=ncdim_sizes[ncdim_idx], stride=1))
                # handle  single index condition
                elif str.isdigit(dim):
                    if int(dim) == 0:
                        ranges.append(grpc_msg.Range(size=1, stride=1))
                    else:
                        ranges.append(grpc_msg.Range(start=int(dim), size=1, stride=1))
                # else, unpack the range
                else:
                    range_attr = ["start", "size", "stride"]
                    rng = grpc_msg.Range()
                    start, end, *stride = [int(i) for i in dim.split(":")]
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
            varName = var_spec
            section = grpc_msg.Section(ranges=[grpc_msg.Range(size=size, stride=1) for size in ncdim_sizes])  

        return varName, section


class netCDF_Encode(gRPC_netCDF):

    def __init__(self):
        super().__init__()

    ## HIGH LEVEL REQUEST STUFF

    def GenerateHeaderFromRequest(self, request):
        nc = nc4.Dataset(request.location)
        nc.set_auto_maskandscale(False)
        error = self.GenerateError()  # BONE this is dummy, need to figure out error handling
        version = 1 # BONE, this is dummy
        # BONE need to include title, id in header
        header = grpc_msg.Header(location=request.location,
                root = self.EncodeGroup(nc)
                )
        return grpc_msg.HeaderResponse(error=error,
                version=version,
                header=header)

    def GenerateDataFromRequest(self, request):
        nc = nc4.Dataset(request.location)
        nc.set_auto_maskandscale(False)
        error = self.GenerateError()  # BONE this is dummy, need to figure out error handling
        version = 1 # BONE, this is dummy
        location = request.location
        variable_spec = request.variable_spec
        varName, section = self.InterpretSpec(request.variable_spec, [dim.size for dim in nc.dimensions.values()])
        var_full_name = nc.variables[varName].group().name + nc.variables[varName].name
        slices = self.InterpretSection(section)
        variable = nc.variables[varName][(*slices,)]
        data_type = self.GetGRPCType(variable.dtype.type)
        data = self.EncodeData(variable, data_type)

        return grpc_msg.DataResponse(error=error,
                version=version,
                location=location,
                variable_spec=variable_spec,
                var_full_name=var_full_name,
                section=section,
                data=data)

    ## GROUP STUFF
    def EncodeGroup(self, group):
        name = group.name
        dims = self.EncodeDimension(group)
        dim_names = [dim.name for dim in dims]
        variables = [
                self.EncodeVariable(variable) if variable.name in dim_names 
                else self.EncodeVariable(variable, coords_only=True)
                for variable in group.variables.values()
                ]
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

    def EncodeVariable(self, variable, coords_only=False):
        name = variable.name
        shapes = self.EncodeDimension(variable)
        atts = self.EncodeAttributes(variable)
        data_type = self.GetGRPCType(variable.dtype.type)
        data = self.EncodeData(variable, data_type) if not coords_only else grpc_msg.Data()
        return grpc_msg.Variable(name=name,
                data_type=data_type,
                shapes=shapes,
                atts=atts,
                data=data)

    ## ATTRIBUTE STUFF
    def EncodeAttributes(self, obj):
        attributes = []
        for attribute_name in obj.ncattrs():
            attribute = obj.getncattr(attribute_name)
            data_type = self.GetAttributeType(attribute)
            data = self.EncodeData(attribute, data_type)
            if isinstance(attribute, str):
                length = 0
            else:
                if np.isscalar(attribute):
                    length=0
                else:
                    length = len(attribute)
            attributes.append(grpc_msg.Attribute(name=attribute_name,
                data_type=data_type,
                length=length,
                data=data))
        return attributes

    def GetAttributeType(self, attribute):
        if np.isscalar(attribute):
            if issubclass(type(attribute), np.number):
                data_type = attribute.dtype.type
            else:
                data_type = type(attribute)
        else:
            if isinstance(attribute, np.ndarray):
                data_type = attribute.dtype.type
            else:
                data_type = type(attribute[0])  # BONE this seems fragile
        
        return self.GetGRPCType(data_type)

    ## DATA STUFF
    def EncodeData(self, obj, data_type):
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
        dtype = self.GetMessageDataType(data_type)
        dmsg = grpc_msg.Data(data_type=data_type, shapes=shapes)
        getattr(dmsg, dtype).extend(data) # get attr returns and iter object which we can then extend code onto
        return dmsg

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

    def EncodeDimensionGroup(self, group):
        dimension_list = []
        for dimension in group.dimensions.values():
            dimension_list.append(grpc_msg.Dimension(
                name=dimension.name,
                length=dimension.size,
                is_unlimited=dimension.isunlimited(),
                ))
        return dimension_list

    def EncodeDimensionVariable(self, variable):
        return [grpc_msg.Dimension(name=name, length=length) for name, length in zip(variable.dimensions, variable.shape)]
    
class netCDF_Decode(gRPC_netCDF):

    def __init__(self):
        super().__init__()
        self.ds = xr.Dataset()

    # high level decode stuff
    def GenerateFileFromResponse(self, header, data):

        # unpack header
        headerError = header.error  # bone add in error handling
        headerVersion = header.version
        
        # unpack data
        dataError = data.error  # bone add in error handling
        dataVersion = data.version
        dataLocation = data.location
        varName, section = self.InterpretSpec(data.variable_spec, [dim.length for dim in header.header.root.dims])
        slice_dict = dict(zip([dim.name for dim in header.header.root.dims], self.InterpretSection(section)))
        dataVariableFullName = data.var_full_name.strip("/")  # BONE how to handle this

        # decode data
        self.DecodeResponse(header.header.root, varName, data.data, slice_dict)

        return self.ds

    def DecodeResponse(self, group, varName, data, slice_dict):
        # assign dimensions, update attributes
        # coordinates are stored as variables so we process them when iterating through vars
        self.ds.attrs.update({attr.name:self.DecodeData(attr.data) for attr in group.atts})  # this returns list of data

        for var in group.vars:

            # first handle coordinates
            if var.name in [dim.name for dim in group.dims]:
                coord_data = self.DecodeData(var.data)
                coord_data = [coord_data] if isinstance(coord_data, int) else list(coord_data)
                self.ds = self.ds.expand_dims(dim={var.name:coord_data[slice_dict[var.name]]})

            if var.name == varName:
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

def bone_func():
    encoder = netCDF_Encode()
    loc = '/Users/rmcmahon/dev/netcdf-grpc/src/data/test3.nc'
    spec = "analysed_sst(0,100:102,121:125)"
    #spec = "analysed_sst"
    header_request = grpc_msg.HeaderRequest(location=loc)
    header_response = encoder.GenerateHeaderFromRequest(header_request)
    data_request = grpc_msg.DataRequest(location=loc, variable_spec=spec)
    data_response = encoder.GenerateDataFromRequest(data_request)

    decoder = netCDF_Decode()
    nf = decoder.GenerateFileFromResponse(header_response, data_response)
    print(nf)
    return nf, header_response, data_response

if __name__ == '__main__':
    bone_func()
    print("ran no errors")
