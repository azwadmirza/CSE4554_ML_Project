    def _api_call(self, apikey, params=None, results_per_page=300, offset=0):
        """Call provider API."""
        parsed_json = {}

        try:
            server = jsonrpclib.Server(self.urls['base_url'])
            parsed_json = server.getTorrents(apikey, params or {}, int(results_per_page), int(offset))
            time.sleep(cpu_presets[app.CPU_PRESET])
        except jsonrpclib.jsonrpc.ProtocolError as error:
            if error.message[1] == 'Invalid API Key':
                logger.log('Incorrect authentication credentials.', logger.WARNING)
            elif error.message[1] == 'Call Limit Exceeded':
                logger.log('You have exceeded the limit of 150 calls per hour.', logger.WARNING)
            else:
                logger.log('JSON-RPC protocol error while accessing provider. Error: {msg!r}'.format
                           (msg=error.message[1]), logger.ERROR)

        except (socket.error, socket.timeout, ValueError) as error:
            logger.log('Error while accessing provider. Error: {msg}'.format
                       (msg=error), logger.WARNING)
        return parsed_json