    def __call__(self, *args, **kwargs):
        logger = get_logger(__name__)

        def handle_sigterm(signum, frame):
            logger.info('SIGTERM received, waiting till the task finished')

        signal.signal(signal.SIGTERM, handle_sigterm)
        _task_stack.push(self)
        self.push_request(args=args, kwargs=kwargs)
        try:
            return self.run(*args, **kwargs)
        finally:
            self.pop_request()
            _task_stack.pop()