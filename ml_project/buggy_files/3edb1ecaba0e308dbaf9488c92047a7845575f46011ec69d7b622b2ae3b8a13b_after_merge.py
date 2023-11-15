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
            code, message = normalize_protocol_error(error)
            if (code, message) == (-32001, 'Invalid API Key'):
                log.warning('Incorrect authentication credentials.')
            elif (code, message) == (-32002, 'Call Limit Exceeded'):
                log.warning('You have exceeded the limit of 150 calls per hour.')
            elif code in (500, 524):
                log.warning('Provider is currently unavailable. Error: {code} {text}',
                            {'code': code, 'text': message})
            else:
                log.error('JSON-RPC protocol error while accessing provider. Error: {msg!r}',
                          {'msg': error.args})

        except (socket.error, ValueError) as error:
            log.warning('Error while accessing provider. Error: {msg!r}', {'msg': error})
        return parsed_json