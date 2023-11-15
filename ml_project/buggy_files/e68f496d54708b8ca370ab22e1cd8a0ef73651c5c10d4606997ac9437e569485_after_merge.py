    def __init__(self, client_conn, server_conn, handshake_flow, live=None):
        super().__init__("websocket", client_conn, server_conn, live)
        self.messages = []  # type: List[WebSocketMessage]
        self.close_sender = 'client'
        self.close_code = '(status code missing)'
        self.close_message = '(message missing)'
        self.close_reason = 'unknown status code'

        if handshake_flow:
            self.client_key = websockets.get_client_key(handshake_flow.request.headers)
            self.client_protocol = websockets.get_protocol(handshake_flow.request.headers)
            self.client_extensions = websockets.get_extensions(handshake_flow.request.headers)
            self.server_accept = websockets.get_server_accept(handshake_flow.response.headers)
            self.server_protocol = websockets.get_protocol(handshake_flow.response.headers)
            self.server_extensions = websockets.get_extensions(handshake_flow.response.headers)
        else:
            self.client_key = ''
            self.client_protocol = ''
            self.client_extensions = ''
            self.server_accept = ''
            self.server_protocol = ''
            self.server_extensions = ''

        self.handshake_flow = handshake_flow