import grpc
import protogen.gcdm_netcdf_pb2 as grpc_msg
import protogen.gcdm_server_pb2_grpc as grpc_server
from netcdf_decode import netCDF_Decode

def run():
    with grpc.insecure_channel('localhost:1234') as channel:
        stub = grpc_server.GcdmStub(channel)
        loc = '/test/data/test3.nc'
        variable_spec = "analysed_sst"
        requestMsg = grpc_msg.HeaderRequest(location=loc)
        dataMsg = grpc_msg.DataRequest(location=loc, variable_spec=variable_spec)
        header = stub.GetNetcdfHeader(requestMsg)
        data = stub.GetNetcdfData(dataMsg)
        return decode_response(header, data)

def decode_response(header, data):
    decoder = netCDF_Decode
    return decoder.GenerateFileFromResponse(header, data)


if __name__ == '__main__':
    run()
