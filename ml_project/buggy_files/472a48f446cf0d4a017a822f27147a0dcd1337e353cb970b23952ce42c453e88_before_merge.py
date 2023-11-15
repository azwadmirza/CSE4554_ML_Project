def bk_worker():
    io_loop = IOLoop.current()
    server = BaseServer(io_loop, bokeh_tornado, bokeh_http)
    server.start()
    server.io_loop.start()