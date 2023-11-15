    def _notify_kodi(self, title, message, host=None, username=None, password=None,
                     force=False, dest_app='KODI'):
        """Private wrapper for the notify_snatch and notify_download functions.

        Detects JSON-RPC version then branches the logic for either the JSON-RPC or legacy HTTP API methods.

        Args:
            message: Message body of the notice to send
            title: Title of the notice to send
            host: KODI webserver host:port
            username: KODI webserver username
            password: KODI webserver password
            force: Used for the Test method to override config saftey checks

        Returns:
            Returns a list results in the format of host:ip:result
            The result will either be 'OK' or False, this is used to be parsed by the calling function.

        """
        # fill in omitted parameters
        if not host:
            host = app.KODI_HOST
        if not username:
            username = app.KODI_USERNAME
        if not password:
            password = app.KODI_PASSWORD

        # Sanitize host when not passed as a list
        if isinstance(host, (string_types, text_type)):
            host = host.split(',')

        # suppress notifications if the notifier is disabled but the notify options are checked
        if not app.USE_KODI and not force:
            log.debug(u'Notification for {app} not enabled, skipping this notification',
                      {'app': dest_app})
            return False

        result = ''
        for cur_host in [x.strip() for x in host if x.strip()]:
            log.debug(u'Sending {app} notification to {host} - {msg}',
                      {'app': dest_app, 'host': cur_host, 'msg': message})

            kodi_api = self._get_kodi_version(cur_host, username, password, dest_app)
            if kodi_api:
                if kodi_api <= 4:
                    log.warning(u'Detected {app} version <= 11, this version is not supported by Medusa. '
                                u'Please upgrade to the Kodi 12 or above.',
                                {'app': dest_app})
                else:
                    log.debug(u'Detected {app} version >= 12, using {app} JSON API',
                              {'app': dest_app})
                    command = {
                        'jsonrpc': '2.0',
                        'method': 'GUI.ShowNotification',
                        'params': {
                            'title': title.encode('utf-8'),
                            'message': message.encode('utf-8'),
                            'image': app.LOGO_URL,
                        },
                        'id': '1',
                    }
                    notify_result = self._send_to_kodi(command, cur_host, username, password, dest_app)
                    if notify_result and notify_result.get('result'):
                        result += cur_host + ':' + notify_result['result'].decode('utf-8')
            else:
                if app.KODI_ALWAYS_ON or force:
                    log.warning(
                        u'Failed to detect {app} version for {host},'
                        u' check configuration and try again.',
                        {'app': dest_app, 'host': cur_host}
                    )
                result += cur_host + ':False'

        return result