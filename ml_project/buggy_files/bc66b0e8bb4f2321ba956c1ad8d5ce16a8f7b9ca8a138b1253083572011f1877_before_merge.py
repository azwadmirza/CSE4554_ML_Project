        def event_stream(handler, pipe):
            '''
            An iterator to return Salt events (and optionally format them)
            '''
            # blocks until send is called on the parent end of this pipe.
            pipe.recv()

            event = salt.utils.event.get_event(
                    'master',
                    sock_dir=self.opts['sock_dir'],
                    transport=self.opts['transport'],
                    opts=self.opts,
                    listen=True)
            stream = event.iter_events(full=True)
            SaltInfo = event_processor.SaltInfo(handler)
            while True:
                data = next(stream)
                if data:
                    try:  # work around try to decode catch unicode errors
                        if 'format_events' in kwargs:
                            SaltInfo.process(data, salt_token, self.opts)
                        else:
                            handler.send('data: {0}\n\n'.format(
                                json.dumps(data)), False)
                    except UnicodeDecodeError:
                        logger.error(
                                "Error: Salt event has non UTF-8 data:\n{0}"
                                .format(data))
                time.sleep(0.1)