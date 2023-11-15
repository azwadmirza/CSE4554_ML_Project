    def resend_activation_email(self, trans, email, username):
        """
        Function resends the verification email in case user wants to log in with an inactive account or he clicks the resend link.
        """
        if email is None:  # User is coming from outside registration form, load email from trans
            email = trans.user.email
        if username is None:  # User is coming from outside registration form, load email from trans
            username = trans.user.username
        is_activation_sent = self.user_manager.send_activation_email(trans, email, username)
        if is_activation_sent:
            message = 'This account has not been activated yet. The activation link has been sent again. Please check your email address <b>%s</b> including the spam/trash folder. <a target="_top" href="%s">Return to the home page</a>.' % (escape(email), url_for('/'))
        else:
            message = 'This account has not been activated yet but we are unable to send the activation link. Please contact your local Galaxy administrator. <a target="_top" href="%s">Return to the home page</a>.' % url_for('/')
            if trans.app.config.error_email_to is not None:
                message += ' Error contact: %s.' % trans.app.config.error_email_to
        return message, is_activation_sent