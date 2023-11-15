    def __new__(cls, opts, **kwargs):
        '''
        Only create one instance of channel per __key()
        '''

        # do we have any mapping for this io_loop
        io_loop = kwargs.get('io_loop')
        if io_loop is None:
            zmq.eventloop.ioloop.install()
            io_loop = tornado.ioloop.IOLoop.current()
        if io_loop not in cls.instance_map:
            cls.instance_map[io_loop] = weakref.WeakValueDictionary()
        loop_instance_map = cls.instance_map[io_loop]

        key = cls.__key(opts, **kwargs)
        if key not in loop_instance_map:
            log.debug('Initializing new AsyncZeroMQReqChannel for {0}'.format(key))
            # we need to make a local variable for this, as we are going to store
            # it in a WeakValueDictionary-- which will remove the item if no one
            # references it-- this forces a reference while we return to the caller
            new_obj = object.__new__(cls)
            new_obj.__singleton_init__(opts, **kwargs)
            loop_instance_map[key] = new_obj
            log.trace('Inserted key into loop_instance_map id {0} for key {1} and process {2}'.format(id(loop_instance_map), key, os.getpid()))
        else:
            log.debug('Re-using AsyncZeroMQReqChannel for {0}'.format(key))
        try:
            return loop_instance_map[key]
        except KeyError:
            # In iterating over the loop_instance_map, we may have triggered
            # garbage collection. Therefore, the key is no longer present in
            # the map. Re-gen and add to map.
            log.debug('Initializing new AsyncZeroMQReqChannel due to GC for {0}'.format(key))
            new_obj = object.__new__(cls)
            new_obj.__singleton_init__(opts, **kwargs)
            loop_instance_map[key] = new_obj
            return loop_instance_map[key]