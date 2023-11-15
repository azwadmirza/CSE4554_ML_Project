    def __init__(self, config=None, args=None):
        # password_dict is a dict (JSON compliant)
        # {'host': 'password', ... }
        # Load the configuration file
        self._password_dict = self.load(config)