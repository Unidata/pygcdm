import grpc
import gen.gcdm_netcdf_pb2 as grpc_msg
import gen.gcdm_server_pb2_grpc as grpc_server
import netcdf_encode

def run():
    with grpc.insecure_channel('localhost:1234') as channel:
        stub = grpc_server.GcdmStub(channel)
        # argument options
        #response = stub.GetNetcdfData()
        #response = stub.GetNetcdfHeader()
        loc = '/Users/rmcmahon/dev/netcdf-grpc/src/data/test3.nc'
        variable_spec = "analysed_sst"
        requestMsg = grpc_msg.HeaderRequest(location=loc)
        dataMsg = grpc_msg.DataRequest(location=loc, variable_spec=variable_spec)
        header = stub.GetNetcdfHeader(requestMsg)
        data = stub.GetNetcdfData(dataMsg)

        # BONE sign off - do some stuff, need to implement then encode/decode stuff

if __name__ == '__main__':
    run()
