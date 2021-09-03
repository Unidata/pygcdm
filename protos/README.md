## Generating Python Source Code from `proto` Files
In order to generate the grpc python source code from the `.proto` files in this folder, we need to use the `protoc` compiler. This can be installed by following the instructions [here](https://www.grpc.io/docs/languages/python/basics/#generating-client-and-server-code). 

To compile our code, and put the resulting functions into `src/proto_gen`, we can use the following commands:
```
$ python -m grpc_tools.protoc -I. --python_out=../src/proto_gen/ --grpc_python_out=../src/proto_gen/ gcdm_grid.proto
$ python -m grpc_tools.protoc -I. --python_out=../src/proto_gen/ --grpc_python_out=../src/proto_gen/ gcdm_netcdf.proto
$ python -m grpc_tools.protoc -I. --python_out=../src/proto_gen/ --grpc_python_out=../src/proto_gen/ gcdm_server.proto
```

More information on the `protoc` compiler can be found by loading the module in python and using the `help` command:
```
$ python
>>> import grpc_tools.protoc
>>> help(grpc_tools.protoc)
```
