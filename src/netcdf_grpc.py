from proto_gen import gcdm_netcdf_pb2 as grpc_msg
import numpy as np

class gRPC_netCDF():
    def __init__(self):
        self.type_dict = self.GenTypeDict()
        self.message_dict = self.GenMessageTypeDict()

    def GenTypeDict(self):
        # BONE work in progress
        return {
                # native python types
                int: grpc_msg.DATA_TYPE_INT,
                str: grpc_msg.DATA_TYPE_STRING,
                float: grpc_msg.DATA_TYPE_FLOAT,

                np.int8: grpc_msg.DATA_TYPE_INT,
                np.int16: grpc_msg.DATA_TYPE_INT,
                np.int32: grpc_msg.DATA_TYPE_INT,
                np.int64: grpc_msg.DATA_TYPE_LONG,

                np.float16: grpc_msg.DATA_TYPE_FLOAT,
                np.float32: grpc_msg.DATA_TYPE_FLOAT,
                np.float64: grpc_msg.DATA_TYPE_FLOAT,

                np.byte: grpc_msg.DATA_TYPE_INT,  # np.byte defaults to np.int8 which causes trouble
                np.ubyte: grpc_msg.DATA_TYPE_UBYTE,
                np.short: grpc_msg.DATA_TYPE_SHORT,
                np.ushort: grpc_msg.DATA_TYPE_USHORT,
                np.double: grpc_msg.DATA_TYPE_DOUBLE,

                np.uint8: grpc_msg.DATA_TYPE_UBYTE,
                np.uint16: grpc_msg.DATA_TYPE_USHORT,
                np.uint32: grpc_msg.DATA_TYPE_UINT,
                np.uint64: grpc_msg.DATA_TYPE_ULONG,
                np.uint: grpc_msg.DATA_TYPE_ULONG,
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
            return self.type_dict[data_type]
        except:
            raise NotImplementedError("Type not supported")

    def GetMessageDataType(self, data_type):
        # find data type to pack message, error if data_type not found in dict
        try:
            return self.message_dict[data_type]
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


