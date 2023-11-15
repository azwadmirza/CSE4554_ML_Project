    def _parse_port_channels_summary(self, lag_type, lag_summary):
        if lag_type == self.MLAG_TYPE:
            if self._os_version >= self.ONYX_API_VERSION:
                found_summary = False
                for summary_item in lag_summary:
                    if self.MLAG_SUMMARY in summary_item:
                        lag_summary = summary_item[self.MLAG_SUMMARY]
                        if lag_summary:
                            lag_summary = lag_summary[0]
                        else:
                            lag_summary = dict()
                        found_summary = True
                        break
                if not found_summary:
                    lag_summary = dict()
            else:
                lag_summary = lag_summary.get(self.MLAG_SUMMARY, dict())
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