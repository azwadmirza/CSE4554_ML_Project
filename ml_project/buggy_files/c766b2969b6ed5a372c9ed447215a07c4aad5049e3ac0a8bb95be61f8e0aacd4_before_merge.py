    def _parse_port_channels_summary(self, lag_type, lag_summary):
        if lag_type == self.MLAG_TYPE:
            lag_summary = lag_summary.get('MLAG Port-Channel Summary', {})
        for lag_key, lag_data in iteritems(lag_summary):
            lag_name, state = self._extract_lag_name(lag_key)
            if not lag_name:
                continue
            lag_members = self._extract_lag_members(lag_type, lag_data[0])
            lag_obj = dict(
                name=lag_name,
                state=state,
                members=lag_members
            )
            self._current_config[lag_name] = lag_obj