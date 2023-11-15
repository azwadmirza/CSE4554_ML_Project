    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.auth_key = self.username if self.username else 'default'