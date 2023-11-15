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
            serial = None
            if command == 'PUSH_ACTIVITY':
                #  Last_Alexa Updated
                serial = (json_payload
                          ['key']
                          ['entryId']).split('#')[2]
                last_called = {
                    'serialNumber': serial,
                    'timestamp': json_payload['timestamp']
                    }
                update_last_called(login_obj, last_called)
            elif command == 'PUSH_AUDIO_PLAYER_STATE':
                # Player update
                serial = (json_payload['dopplerId']['deviceSerialNumber'])
                _LOGGER.debug("Updating media_player: %s", json_payload)
                hass.bus.fire(('{}_{}'.format(DOMAIN,
                                              hide_email(email)))[0:32],
                              {'player_state': json_payload})
            elif command == 'PUSH_VOLUME_CHANGE':
                # Player volume update
                serial = (json_payload['dopplerId']['deviceSerialNumber'])
                _LOGGER.debug("Updating media_player volume: %s", json_payload)
                hass.bus.fire(('{}_{}'.format(DOMAIN,
                                              hide_email(email)))[0:32],
                              {'player_state': json_payload})
            elif command == 'PUSH_DOPPLER_CONNECTION_CHANGE':
                # Player availability update
                serial = (json_payload['dopplerId']['deviceSerialNumber'])
                _LOGGER.debug("Updating media_player availability %s",
                              json_payload)
                hass.bus.fire(('{}_{}'.format(DOMAIN,
                                              hide_email(email)))[0:32],
                              {'player_state': json_payload})
            if (serial and serial not in (hass.data[DATA_ALEXAMEDIA]
                                          ['accounts']
                                          [email]
                                          ['entities']
                                          ['media_player'].keys())):
                _LOGGER.debug("Discovered new media_player %s", serial)
                (hass.data[DATA_ALEXAMEDIA]
                 ['accounts'][email]['new_devices']) = True
                update_devices(no_throttle=True)