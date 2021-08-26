import gen.gcdm_netcdf_pb2 as grpc_msg
import importlib
import netcdf_encode

def dummy_run():
    importlib.reload(netcdf_encode)
    encoder = netcdf_encode.netCDF_Encode()
    request = grpc_msg.HeaderRequest(location='/Users/rmcmahon/dev/netcdf-grpc/src/data/test3.nc')
    encoder.GenerateHeaderFromRequest(request)

if __name__ == '__main__':
    dummy_run()
