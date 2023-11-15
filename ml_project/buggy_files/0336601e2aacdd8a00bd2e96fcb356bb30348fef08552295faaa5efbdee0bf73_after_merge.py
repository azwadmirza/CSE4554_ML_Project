    def on_manager_state_changed(self, state):
        if not state:
            self._unregister_agent()