## Running redis cache server
```
$ mkdir build && cd build
$ cmake ../
$ make
$ ./exec/redis_server [port]
```

## Running redis cache client
```
$ cd client
$ python redis_client.py --ip_addr=[ip address] --port=[port]
```

## References
- [redis cache implementation](https://build-your-own.org/redis/#table-of-contents)