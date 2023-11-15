    def _send_growl(self, options, message=None):

        # Initialize Notification
        notice = gntp.core.GNTPNotice(
            app=options['app'],
            name=options['name'],
            title=options['title'],
            password=options['password'],
        )

        # Optional
        if options['sticky']:
            notice.add_header('Notification-Sticky', options['sticky'])
        if options['priority']:
            notice.add_header('Notification-Priority', options['priority'])
        if options['icon']:
            notice.add_header('Notification-Icon', app.LOGO_URL)

        if message:
            notice.add_header('Notification-Text', message)

        response = self._send(options['host'], options['port'], notice.encode('utf-8'), options['debug'])
        return True if isinstance(response, gntp.core.GNTPOK) else False