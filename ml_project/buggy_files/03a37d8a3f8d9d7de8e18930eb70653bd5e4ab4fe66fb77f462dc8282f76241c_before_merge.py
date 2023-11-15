    def __init__(self, name, default_state=False, wipe_action=None):
        self.name = name
        self.state = default_state
        self.wipe_action = wipe_action
        self.is_dependent = self.wipe_action.is_dependent