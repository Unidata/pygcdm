import gen.gcdm_netcdf_pb2 as grpc_msg
import netCDF4 as nc4
import xarray as xr
import numpy as np
import os

class gRPC():
    def __init__(self):
        self.typeDict = self.GenTypeDict()
    
    def GenTypeDict(self):
        # BONE work in progress
        # BONE, add in numpy types
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
    

    def GetGRPCType(self, val_type):
        try:
            return self.typeDict(val_type)
        except:
            raise NotImplementedError("Type not supported")

    def GenerateDimensionsFromVariable(self, variable):


    def GenerateDataFromAttribute(self, attribute):
        data_type = self.GetGRPCType(attribute)
        if isinstance(data_type, grpc_msg.DATA_TYPE_BYTE):
            return grpc_msg.Data(data_type=data_type, bdata=attribute)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_SHORT, grpc_msg.DATA_TYPE_INT)):
            return grpc_msg.Data(data_type=data_type, idata=attribute)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_USHORT, grpc_msg.DATA_TYPE_UINT)):
            return grpc_msg.Data(data_type=data_type, uidata=attribute)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_LONG)):
            return grpc_msg.Data(data_type=data_type, ldata=attribute)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_ULONG)):
            return grpc_msg.Data(data_type=data_type, uldata=attribute)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_FLOAT)):
            return grpc_msg.Data(data_type=data_type, fdata=attribute)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_DOUBLE)):
            return grpc_msg.Data(data_type=data_type, ddata=attribute)
        elif isinstance(data_type, (grpc_msg.DATA_TYPE_STRING)):
            return grpc_msg.Data(data_type=data_type, sdata=attribute)
        else:
            raise NotImplementedError("Attribute data type not supported")

    def GenerateDataFromVariable(self, variable):
        name = variable.name
        data_type = self.GetGRPCType(variable.dtype)
        shapes = 


    def GenerateError(self):
        # BONE idea:
        # 1. check for errors with java implementation
        # 2. this should probably broken out into a grpc parent class
        message = "Dummy error" # bone
        code = 0
        return grpc_msg.Error(message=message, code=code)

class gRPC_Header(gRPC):
    def __init__(self, headerRequest):
        super().__init__()
        self.location = headerRequest.location
        self.nc = nc4.Dataset(self.location)
    
    def HeaderResponse(self):
        error = self.GenerateError()
        version = 1 # bone
        header = self.GenerateHeader()
        return grpc_msg.HeaderResponse(error=error,
                                       version=version,
                                       header=header)

    def GenerateHeader():
        location = self.location
        title = self.nc.title
        msg_id = self.nc.id
        root = self.GenerateGroup("/")
        return grpc_msg.Header(location=location,
                               title=title,
                               id=msg_id,
                               root=root)
    
    def GenerateGroup(self, path):
        # bone, path should allow for subgroups
        if path == "/":
            nc = self.nc
        else:
            pass
       
        name = nc.name
        dims = [grpc_msg.Dimension(name=k, length=v.size, is_unlimited=v.isunlimited()) for k,v in list(nc.dimensions.items())] # bone, need to  support other bool stuff in msg type
        # the problem with this is that nc.dimensions returns a dict and nc.variables['thing'] is a netCDF4.Variable. Could handle conditionally? 
        variables = []
        for name in nc.variables.keys():
            # get variable data type
            data_type = nc.variables[name].dtype

            # BONE NOTES:
            #   breakout dimension into separate method that generically can produce based on input type (variable vs dataset)
            # get variable dimensions
            var_dims = [grpc_msg.Dimension(name=name, length=size) for name, size in zip(nc.variables[asst].dimensions, nc.variables[asst].shape)]

            # get attributes
            for attr in nc.variables[name].ncattrs():
                data_type = self.GetGRPCType(type(nc.variables[name].getncattr(attr)))
                if isinstance(nc.variables[name].getncattr(attr), list):
                    length = len(nc.variables[name].getncattr(attr))
                else:
                    length = 0
                data = self.GenerateDataFromAttribute(nc.variables[name].getncattr(attr))




class gRPC_Data():
    pass
if __name__=="__main__":
    hr = grpc_msg.HeaderRequest(location="test2.nc")
    header = gRPC_Header(hr)
