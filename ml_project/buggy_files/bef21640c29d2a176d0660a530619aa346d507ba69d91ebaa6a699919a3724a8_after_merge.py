    def _api_call(self, params=None, results_per_page=300, offset=0):
        """Call provider API."""
        parsed_json = {}

        try:
            server = jsonrpclib.Server(self.urls['base_url'])
            parsed_json = server.getTorrents(
                self.api_key,
                params or {},
                int(results_per_page),
                int(offset)
            )
            time.sleep(cpu_presets[app.CPU_PRESET])
        except jsonrpclib.jsonrpc.ProtocolError as error:
            message = error.args[0]
            if message == (-32001, 'Invalid API Key'):
                log.warning('Incorrect authentication credentials.')
            elif message == (-32002, 'Call Limit Exceeded'):
                log.warning('You have exceeded the limit of 150 calls per hour.')
            elif isinstance(message, tuple) and message[1] in (524, ):
                log.warning('Provider is currently unavailable. Error: {code} {text}',
                            {'code': message[1], 'text': message[2]})
            else:
                log.error('JSON-RPC protocol error while accessing provider. Error: {msg!r}',
                          {'msg': message})

        except (socket.error, ValueError) as error:
            log.warning('Error while accessing provider. Error: {msg!r}', {'msg': error})
        return parsed_json