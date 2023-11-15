    def __init__(self, client_conn, server_conn, handshake_flow, live=None):
        super().__init__("websocket", client_conn, server_conn, live)
        self.messages = []  # type: List[WebSocketMessage]
        self.close_sender = 'client'
        self.close_code = '(status code missing)'
        self.close_message = '(message missing)'
        self.close_reason = 'unknown status code'
        self.handshake_flow = handshake_flow