# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from pygcdm.protogen import gcdm_grid_pb2 as pygcdm_dot_protogen_dot_gcdm__grid__pb2
from pygcdm.protogen import gcdm_netcdf_pb2 as pygcdm_dot_protogen_dot_gcdm__netcdf__pb2


class GcdmStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetNetcdfHeader = channel.unary_unary(
                '/ucar.gcdm.Gcdm/GetNetcdfHeader',
                request_serializer=pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.HeaderRequest.SerializeToString,
                response_deserializer=pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.HeaderResponse.FromString,
                )
        self.GetNetcdfData = channel.unary_stream(
                '/ucar.gcdm.Gcdm/GetNetcdfData',
                request_serializer=pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.DataRequest.SerializeToString,
                response_deserializer=pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.DataResponse.FromString,
                )
        self.GetGridDataset = channel.unary_unary(
                '/ucar.gcdm.Gcdm/GetGridDataset',
                request_serializer=pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDatasetRequest.SerializeToString,
                response_deserializer=pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDatasetResponse.FromString,
                )
        self.GetGridData = channel.unary_stream(
                '/ucar.gcdm.Gcdm/GetGridData',
                request_serializer=pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDataRequest.SerializeToString,
                response_deserializer=pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDataResponse.FromString,
                )


class GcdmServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetNetcdfHeader(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetNetcdfData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetGridDataset(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetGridData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GcdmServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetNetcdfHeader': grpc.unary_unary_rpc_method_handler(
                    servicer.GetNetcdfHeader,
                    request_deserializer=pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.HeaderRequest.FromString,
                    response_serializer=pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.HeaderResponse.SerializeToString,
            ),
            'GetNetcdfData': grpc.unary_stream_rpc_method_handler(
                    servicer.GetNetcdfData,
                    request_deserializer=pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.DataRequest.FromString,
                    response_serializer=pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.DataResponse.SerializeToString,
            ),
            'GetGridDataset': grpc.unary_unary_rpc_method_handler(
                    servicer.GetGridDataset,
                    request_deserializer=pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDatasetRequest.FromString,
                    response_serializer=pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDatasetResponse.SerializeToString,
            ),
            'GetGridData': grpc.unary_stream_rpc_method_handler(
                    servicer.GetGridData,
                    request_deserializer=pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDataRequest.FromString,
                    response_serializer=pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDataResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ucar.gcdm.Gcdm', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Gcdm(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetNetcdfHeader(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ucar.gcdm.Gcdm/GetNetcdfHeader',
            pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.HeaderRequest.SerializeToString,
            pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.HeaderResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetNetcdfData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ucar.gcdm.Gcdm/GetNetcdfData',
            pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.DataRequest.SerializeToString,
            pygcdm_dot_protogen_dot_gcdm__netcdf__pb2.DataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetGridDataset(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ucar.gcdm.Gcdm/GetGridDataset',
            pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDatasetRequest.SerializeToString,
            pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDatasetResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetGridData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ucar.gcdm.Gcdm/GetGridData',
            pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDataRequest.SerializeToString,
            pygcdm_dot_protogen_dot_gcdm__grid__pb2.GridDataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
