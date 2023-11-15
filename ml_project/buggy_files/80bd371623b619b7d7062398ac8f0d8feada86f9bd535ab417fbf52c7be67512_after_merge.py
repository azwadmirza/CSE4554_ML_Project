    def notify_user(self, notification, translation_obj,
                    context=None, headers=None):
        '''
        Wrapper for sending notifications to user.
        '''
        if context is None:
            context = {}
        if headers is None:
            headers = {}

        # Check whether user is still allowed to access this project
        if not translation_obj.has_acl(self.user):
            return
        # Actually send notification
        send_notification_email(
            self.language,
            self.user.email,
            notification,
            translation_obj,
            context,
            headers
        )