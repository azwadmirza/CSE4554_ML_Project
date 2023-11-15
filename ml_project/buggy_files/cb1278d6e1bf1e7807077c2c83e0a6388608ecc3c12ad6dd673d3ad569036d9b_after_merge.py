    def refresh(self):
        """Update Guard state."""
        import json
        _LOGGER.debug("%s: Refreshing %s", self.account, self.name)
        state = None
        state_json = self.alexa_api.get_guard_state(self._login,
                                                    self._appliance_id)
        # _LOGGER.debug("%s: state_json %s", self.account, state_json)
        if (state_json and 'deviceStates' in state_json
                and state_json['deviceStates']):
            cap = state_json['deviceStates'][0]['capabilityStates']
            # _LOGGER.debug("%s: cap %s", self.account, cap)
            for item_json in cap:
                item = json.loads(item_json)
                # _LOGGER.debug("%s: item %s", self.account, item)
                if item['name'] == 'armState':
                    state = item['value']
                    # _LOGGER.debug("%s: state %s", self.account, state)
        elif state_json['errors']:
            _LOGGER.debug("%s: Error refreshing alarm_control_panel %s: %s",
                          self.account,
                          self.name,
                          json.dumps(state_json['errors']) if state_json
                          else None)
        if state is None:
            return
        if state == "ARMED_AWAY":
            self._state = STATE_ALARM_ARMED_AWAY
        elif state == "ARMED_STAY":
            self._state = STATE_ALARM_DISARMED
        else:
            self._state = STATE_ALARM_DISARMED
        _LOGGER.debug("%s: Alarm State: %s", self.account, self.state)