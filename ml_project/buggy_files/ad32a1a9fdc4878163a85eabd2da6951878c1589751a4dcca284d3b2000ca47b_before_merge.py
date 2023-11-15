    def load_current_config(self):
        # called in base class in run function
        self._current_config = dict()
        pfc_config = self._get_pfc_config()
        if not pfc_config:
            return
        if 'Table 2' in pfc_config:
            pfc_config = pfc_config['Table 2']
        for if_name, if_pfc_data in iteritems(pfc_config):
            match = self.PFC_IF_REGEX.match(if_name)
            if not match:
                continue
            if if_pfc_data:
                if_pfc_data = if_pfc_data[0]
                self._current_config[if_name] = \
                    self._create_if_pfc_data(if_name, if_pfc_data)