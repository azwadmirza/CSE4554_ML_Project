    def __init__(self, name, generator, args=(), kwargs={}):
        super().__init__()

        self._should_terminate_flag = mp.Value(c_bool, 0)
        self._completed = False
        self._canceled = False

        pipe_recv, pipe_send = mp.Pipe(False)
        wrapper_args = [pipe_send, self._should_terminate_flag, generator]
        wrapper_args.extend(args)
        self.process = mp.Process(target=self._wrapper, name=name, args=wrapper_args, kwargs=kwargs)
        self.process.daemon = True
        self.process.start()
        self.pipe = pipe_recv