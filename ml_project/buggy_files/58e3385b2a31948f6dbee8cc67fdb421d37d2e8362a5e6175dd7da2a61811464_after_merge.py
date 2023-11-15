    def __init__(self, settings):
        self.default_user = settings['FTP_USER']
        self.default_password = settings['FTP_PASSWORD']
        self.passive_mode = settings['FTP_PASSIVE_MODE']