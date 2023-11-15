    def ws_handler(message_obj):
        """Handle websocket messages.

        This allows push notifications from Alexa to update last_called
        and media state.
        """
        command = (message_obj.json_payload['command']
                   if isinstance(message_obj.json_payload, dict) and
                   'command' in message_obj.json_payload
                   else None)
        json_payload = (message_obj.json_payload['payload']
                        if isinstance(message_obj.json_payload, dict) and
                        'payload' in message_obj.json_payload
                        else None)
        if command and json_payload:
            _LOGGER.debug("%s: Received websocket command: %s : %s",
                          hide_email(email),
                          command, json_payload)
            if command == 'PUSH_ACTIVITY':
                #  Last_Alexa Updated
                last_called = {
                    'serialNumber': (json_payload
                                     ['key']
                                     ['entryId']).split('#')[2],
                    'timestamp': json_payload['timestamp']
                    }
                update_last_called(login_obj, last_called)
            elif command == 'PUSH_AUDIO_PLAYER_STATE':
                # Player update
                _LOGGER.debug("Updating media_player: %s", json_payload)
                hass.bus.fire(('{}_{}'.format(DOMAIN,
                                              hide_email(email)))[0:32],
                              {'player_state': json_payload})
            elif command == 'PUSH_VOLUME_CHANGE':
                # Player volume update
                _LOGGER.debug("Updating media_player volume: %s", json_payload)
                hass.bus.fire(('{}_{}'.format(DOMAIN,
                                              hide_email(email)))[0:32],
                              {'player_state': json_payload})
            elif command == 'PUSH_DOPPLER_CONNECTION_CHANGE':
                # Player volume update
                _LOGGER.debug("Updating media_player avalibility %s",
                              json_payload)
                hass.bus.fire(('{}_{}'.format(DOMAIN,
                                              hide_email(email)))[0:32],
                              {'player_state': json_payload})