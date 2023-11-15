    def __new__(cls, socket_path, io_loop=None):
        io_loop = io_loop or tornado.ioloop.IOLoop.current()
        if io_loop not in IPCClient.instance_map:
            IPCClient.instance_map[io_loop] = weakref.WeakValueDictionary()
        loop_instance_map = IPCClient.instance_map[io_loop]

        # FIXME
        key = str(socket_path)

        if key not in loop_instance_map:
            log.debug('Initializing new IPCClient for path: {0}'.format(key))
            new_client = object.__new__(cls)
            # FIXME
            new_client.__singleton_init__(io_loop=io_loop, socket_path=socket_path)
            loop_instance_map[key] = new_client
        else:
            log.debug('Re-using IPCClient for {0}'.format(key))
        return loop_instance_map[key]