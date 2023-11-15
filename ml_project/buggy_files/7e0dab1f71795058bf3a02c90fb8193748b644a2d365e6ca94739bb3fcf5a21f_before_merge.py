    def on_get_chunk(self, interface, response):
        '''Handle receiving a chunk of block headers'''
        error = response.get('error')
        result = response.get('result')
        params = response.get('params')
        if result is None or params is None or error is not None:
            interface.print_error(error or 'bad response')
            return
        # Ignore unsolicited chunks
        index = params[0]
        if interface.request != index:
            return
        connect = interface.blockchain.connect_chunk(index, result)
        # If not finished, get the next chunk
        if not connect:
            self.connection_down(interface.server)
            return
        if interface.blockchain.height() < interface.tip:
            self.request_chunk(interface, index+1)
        else:
            interface.request = None
            interface.mode = 'default'
            interface.print_error('catch up done', interface.blockchain.height())
            interface.blockchain.catch_up = None
        self.notify('updated')