    def _update_magp_data(self, magp_data):
        for magp_item in magp_data:
            magp_id = self.get_magp_id(magp_item)
            inst_data = self._create_magp_instance_data(magp_id, magp_item)
            self._current_config[magp_id] = inst_data