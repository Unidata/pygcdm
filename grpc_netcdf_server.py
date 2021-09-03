import grpc
import os
from src.netcdf_encode import netCDF_Encode
from src.protogen import gcdm_netcdf_pb2 as grpc_msg
from src.protogen import gcdm_server_pb2_grpc as grpc_server
from concurrent import futures

class Responder(grpc_server.GcdmServicer):

    def __init__(self):
        self.encoder = netCDF_Encode()

    def GetNetcdfHeader(self, request, context):
        print("Header Requested")
        return self.encoder.GenerateHeaderFromRequest(request)

    def GetNetcdfData(self, request, context):
        print("Data Requested")

        # stream the data response
        data_response = [self.encoder.GenerateDataFromRequest(request)]
        for data in data_response:
            yield(data)


def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_server.add_GcdmServicer_to_server(Responder(), server)
    server.add_insecure_port('[::]:1234')
    print("starting server...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    server()
