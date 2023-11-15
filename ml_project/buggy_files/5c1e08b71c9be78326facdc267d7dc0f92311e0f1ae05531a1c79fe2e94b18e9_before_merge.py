    def _sendRegistration(self, host=None, password=None):
        opts = {}

        if host is None:
            hostParts = app.GROWL_HOST.split(':')
        else:
            hostParts = host.split(':')

        if len(hostParts) != 2 or hostParts[1] == '':
            port = 23053
        else:
            port = int(hostParts[1])

        opts['host'] = hostParts[0]
        opts['port'] = port

        if password is None:
            opts['password'] = app.GROWL_PASSWORD
        else:
            opts['password'] = password

        opts['app'] = 'Medusa'
        opts['debug'] = False

        # Send Registration
        register = gntp.core.GNTPRegister()
        register.add_header('Application-Name', opts['app'])
        register.add_header('Application-Icon', app.LOGO_URL)

        register.add_notification('Test', True)
        register.add_notification(common.notifyStrings[common.NOTIFY_SNATCH], True)
        register.add_notification(common.notifyStrings[common.NOTIFY_DOWNLOAD], True)
        register.add_notification(common.notifyStrings[common.NOTIFY_GIT_UPDATE], True)

        if opts['password']:
            register.set_password(opts['password'])

        try:
            return self._send(opts['host'], opts['port'], register.encode(), opts['debug'])
        except Exception as error:
            log.warning(
                u'GROWL: Unable to send growl to {host}:{port} - {msg!r}',
                {'msg': ex(error), 'host': opts['host'], 'port': opts['port']}
            )
            return False