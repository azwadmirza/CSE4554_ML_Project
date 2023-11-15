    def __init__(self, server_id=None, api_client=None):

        self.server_id = server_id or None
        self.api_client = api_client
        self.server = self.api_client.config.data['auth.server']
        self.stack = []