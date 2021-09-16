"""Parent class with type conversions and  utilites for encode/decode classes."""

from pygcdm.protogen import gcdm_netcdf_pb2 as grpc_msg
import numpy as np


class gRPC_netCDF():
    """Parent netCDF gRPC class with utility items."""

    def __init__(self):
        """Initialization function that defines dictionaries for gRPC/python type conversions."""
        self.type_dict = {
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

        self.message_dict = {
                grpc_msg.DATA_TYPE_BYTE: 'bdata',
                grpc_msg.DATA_TYPE_SHORT: 'idata',
                grpc_msg.DATA_TYPE_INT: 'idata',
                grpc_msg.DATA_TYPE_USHORT: 'uidata',
                grpc_msg.DATA_TYPE_UINT: 'uidata',
                grpc_msg.DATA_TYPE_LONG: 'ldata',
                grpc_msg.DATA_TYPE_ULONG: 'uldata',
                grpc_msg.DATA_TYPE_FLOAT: 'fdata',
                grpc_msg.DATA_TYPE_DOUBLE: 'ddata',
                grpc_msg.DATA_TYPE_STRING: 'sdata',
                }

    def get_grpc_type(self, data_type):
        """Returns gRPC data type from python data type."""
        try:
            return self.type_dict[data_type]
        except KeyError:
            raise NotImplementedError('Type not supported')

    def get_message_data_type(self, data_type):
        """Returns gRPC `Data` message type field to write into when encoding data"""
        try:
            return self.message_dict[data_type]
        except KeyError:
            raise NotImplementedError('Incorrect message data type')

    def get_version(self):
        """Return version type"""
        # TODO: not implemented
        version = 0
        return version

    def _generate_error(self, error_type=None):
        code = 0  # TODO: not implemented
        error_dict = {
                     None: 'no error',
                     'bad_path': 'Specified file path does not exist',
                     'bad_file': 'Specified file is not a netCDF file',
                     'bad_request_header': 'Message sent is not of type HeaderRequest',
                     'bad_request_data': 'Message sent is not of type DataRequest',
                     'bad_varspec': 'Incorrect variable spec: formatting not understood',
                     'bad_varspec_variable': 'Incorrect variable spec: specified variable does not exist',
                     'bad_varspec_variable_dim_mismatch': 'Incorrect variable spec: number of specified dimensions does not match number of variable dimensions',
                     'bad_varspec_variable_dim_exceed': 'Incorrect variable spec: size of specified dimension(s) exceeds size of specified variable dimension(s)',
                     }

        return grpc_msg.Error(message=error_dict[error_type], code=code)

    def interpret_section(self, section):
        """Return list of python `slice` objects based on gRPC sections."""
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
