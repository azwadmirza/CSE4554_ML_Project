    def register(self, trans, email=None, username=None, password=None, confirm=None, subscribe=False):
        """
        Register a new user.
        """
        if not trans.app.config.allow_user_creation and not trans.user_is_admin:
            message = "User registration is disabled.  Please contact your local Galaxy administrator for an account."
            if trans.app.config.error_email_to is not None:
                message += " Contact: %s" % trans.app.config.error_email_to
            return None, message
        if not email or not username or not password or not confirm:
            return None, "Please provide email, username and password."
        message = "\n".join([validate_email(trans, email),
                             validate_password(trans, password, confirm),
                             validate_publicname(trans, username)]).rstrip()
        if message:
            return None, message
        email = util.restore_text(email)
        username = util.restore_text(username)
        message, status = trans.app.auth_manager.check_registration_allowed(email, username, password)
        if message:
            return None, message
        if subscribe:
            message = self.send_subscription_email(email)
            if message:
                return None, message
        user = self.create(email=email, username=username, password=password)
        if self.app.config.user_activation_on:
            self.send_activation_email(trans, email, username)
        return user, None