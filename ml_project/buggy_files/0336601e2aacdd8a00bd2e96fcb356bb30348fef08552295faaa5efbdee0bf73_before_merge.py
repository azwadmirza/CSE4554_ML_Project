    def on_manager_state_changed(self, state):
        if not state:
            self._agent = None