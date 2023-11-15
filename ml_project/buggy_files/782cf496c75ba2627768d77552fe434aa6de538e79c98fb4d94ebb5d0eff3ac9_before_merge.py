    def received_message(self, message):
        message = json.loads(message.data)
        self.logger.info('<--- {0}'.format(message))
        response = None
        if message['command'] == 'hello':  # Handshake
            response = {
                'command': 'hello',
                'protocols': [
                    'http://livereload.com/protocols/official-7',
                ],
                'serverName': 'nikola-livereload',
            }
        elif message['command'] == 'info':  # Someone connected
            self.logger.info('****** Browser connected: {0}'.format(message.get('url')))
            self.logger.info('****** sending {0} pending messages'.format(len(pending)))
            while pending:
                msg = pending.pop()
                self.logger.info('---> {0}'.format(msg.data))
                self.send(msg, msg.is_binary)
        else:
            response = {
                'command': 'alert',
                'message': 'HEY',
            }
        if response is not None:
            response = json.dumps(response)
            self.logger.info('---> {0}'.format(response))
            response = TextMessage(response)
            self.send(response, response.is_binary)