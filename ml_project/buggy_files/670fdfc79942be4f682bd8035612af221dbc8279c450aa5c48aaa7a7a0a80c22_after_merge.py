    def __validate_login(self, trans, payload={}, **kwd):
        '''Handle Galaxy Log in'''
        if not payload:
            payload = kwd
        message = trans.check_csrf_token(payload)
        if message:
            return self.message_exception(trans, message)
        login = payload.get("login")
        password = payload.get("password")
        redirect = payload.get("redirect")
        status = None
        if not login or not password:
            return self.message_exception(trans, "Please specify a username and password.")
        user = trans.sa_session.query(trans.app.model.User).filter(or_(
            trans.app.model.User.table.c.email == login,
            trans.app.model.User.table.c.username == login
        )).first()
        log.debug("trans.app.config.auth_config_file: %s" % trans.app.config.auth_config_file)
        if user is None:
            message, user = self.__autoregistration(trans, login, password)
            if message:
                return self.message_exception(trans, message)
        elif user.deleted:
            message = "This account has been marked deleted, contact your local Galaxy administrator to restore the account."
            if trans.app.config.error_email_to is not None:
                message += " Contact: %s." % trans.app.config.error_email_to
            return self.message_exception(trans, message, sanitize=False)
        elif user.external:
            message = "This account was created for use with an external authentication method, contact your local Galaxy administrator to activate it."
            if trans.app.config.error_email_to is not None:
                message += " Contact: %s." % trans.app.config.error_email_to
            return self.message_exception(trans, message, sanitize=False)
        elif not trans.app.auth_manager.check_password(user, password):
            return self.message_exception(trans, "Invalid password.")
        elif trans.app.config.user_activation_on and not user.active:  # activation is ON and the user is INACTIVE
            if (trans.app.config.activation_grace_period != 0):  # grace period is ON
                if self.is_outside_grace_period(trans, user.create_time):  # User is outside the grace period. Login is disabled and he will have the activation email resent.
                    message, status = self.resend_activation_email(trans, user.email, user.username)
                    return self.message_exception(trans, message, sanitize=False)
                else:  # User is within the grace period, let him log in.
                    trans.handle_user_login(user)
                    trans.log_event("User logged in")
            else:  # Grace period is off. Login is disabled and user will have the activation email resent.
                message, status = self.resend_activation_email(trans, user.email, user.username)
                return self.message_exception(trans, message, sanitize=False)
        else:  # activation is OFF
            pw_expires = trans.app.config.password_expiration_period
            if pw_expires and user.last_password_change < datetime.today() - pw_expires:
                # Password is expired, we don't log them in.
                return {"message": "Your password has expired. Please reset or change it to access Galaxy.", "status": "warning", "expired_user": trans.security.encode_id(user.id)}
            trans.handle_user_login(user)
            trans.log_event("User logged in")
            if pw_expires and user.last_password_change < datetime.today() - timedelta(days=pw_expires.days / 10):
                # If password is about to expire, modify message to state that.
                expiredate = datetime.today() - user.last_password_change + pw_expires
                return {"message": "Your password will expire in %s day(s)." % expiredate.days, "status": "warning"}
        return {"message": "Success.", "redirect": self.__get_redirect_url(redirect)}