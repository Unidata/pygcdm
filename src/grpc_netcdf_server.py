import grpc
import gen.gcdm_netcdf_pb2 as grpc_msg
import gen.gcdm_server_pb2_grpc as grpc_server
import netcdf_encode
from concurrent import futures

class Responder(grpc_server.GcdmServicer):

    def __init__(self):
        self.loc = '/Users/rmcmahon/dev/netcdf-grpc/src/data/test3.nc'
        self.encoder = netcdf_encode.netCDF_Encode()
        self.decoder = netcdf_encode.netCDF_Decode()

    def GetNetcdfHeader(self, request, context):
        print("Header Requested")
        return self.encoder.GenerateHeaderFromRequest(request)

    def GetNetcdfData(self, request, context):
        print("Data Requested")
        return self.encoder.GenerateDataFromRequest(request)


def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_server.add_GcdmServicer_to_server(Responder(), server)
    server.add_insecure_port('[::]:1234')
    print("starting server...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    server()
