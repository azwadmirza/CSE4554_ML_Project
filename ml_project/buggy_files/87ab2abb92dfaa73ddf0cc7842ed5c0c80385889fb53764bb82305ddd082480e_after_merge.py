    def __init__(self):
        self.updater = None
        self.install_type = None
        self.amActive = False
        self.install_type = self.find_install_type()
        if self.install_type == 'git':
            self.updater = GitUpdateManager()
        elif self.install_type == 'source':
            self.updater = SourceUpdateManager()

        self.session = helpers.make_session()