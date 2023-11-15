    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", '%s://%s%s' % (urlscheme, self.realhost, handler))