    def load_current_config(self):
        # called in base class in run function
        self._current_config = dict()
        magp_data = self._get_magp_config()
        if magp_data:
            self._update_magp_data(magp_data)