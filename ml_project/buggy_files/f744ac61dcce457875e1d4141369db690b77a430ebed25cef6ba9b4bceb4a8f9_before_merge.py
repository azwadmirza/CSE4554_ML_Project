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
            if error.message[1] == 'Invalid API Key':
                log.warning('Incorrect authentication credentials.')
            elif error.message[1] == 'Call Limit Exceeded':
                log.warning('You have exceeded the limit of'
                            ' 150 calls per hour.')
            else:
                log.error('JSON-RPC protocol error while accessing provider.'
                          ' Error: {msg!r}', {'msg': error.message[1]})

        except (socket.error, socket.timeout, ValueError) as error:
            log.warning('Error while accessing provider.'
                        ' Error: {msg}', {'msg': error})
        return parsed_json