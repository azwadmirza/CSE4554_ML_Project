    def _update_magp_data(self, magp_data):
        if self._os_version >= self.ONYX_API_VERSION:
            for magp_config in magp_data:
                for magp_name, data in iteritems(magp_config):
                    magp_id = int(magp_name.replace('MAGP ', ''))
                    self._current_config[magp_id] = \
                        self._create_magp_instance_data(magp_id, data[0])
        else:
            for magp_item in magp_data:
                magp_id = self.get_magp_id(magp_item)
                inst_data = self._create_magp_instance_data(magp_id, magp_item)
                self._current_config[magp_id] = inst_data