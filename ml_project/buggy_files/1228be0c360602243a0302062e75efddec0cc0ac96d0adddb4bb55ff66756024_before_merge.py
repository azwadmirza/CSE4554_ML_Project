        def listen():
            '''
            An iterator to yield Salt events
            '''
            event = salt.utils.event.get_event(
                    'master',
                    sock_dir=self.opts['sock_dir'],
                    transport=self.opts['transport'],
                    opts=self.opts,
                    listen=True)
            stream = event.iter_events(full=True)

            yield u'retry: {0}\n'.format(400)

            while True:
                data = next(stream)
                yield u'tag: {0}\n'.format(data.get('tag', ''))
                yield u'data: {0}\n\n'.format(json.dumps(data))