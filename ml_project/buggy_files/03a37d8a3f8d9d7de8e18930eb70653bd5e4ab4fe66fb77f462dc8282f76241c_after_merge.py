    def __init__(self, name, default_state=False,
                 wipe_action=None, wipe_args=None):
        self.name = name
        self.state = default_state
        self.wipe_action = wipe_action
        self.wipe_args = wipe_args
        self.is_dependent = getattr(self.wipe_action, 'is_dependent', False)