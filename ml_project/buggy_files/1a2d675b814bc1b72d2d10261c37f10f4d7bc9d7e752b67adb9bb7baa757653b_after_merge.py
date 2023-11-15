    def has_feedback(self):
        """ returns whether user has given feedback """
        return self.cli_config.getboolean('core', 'given feedback', fallback='false')