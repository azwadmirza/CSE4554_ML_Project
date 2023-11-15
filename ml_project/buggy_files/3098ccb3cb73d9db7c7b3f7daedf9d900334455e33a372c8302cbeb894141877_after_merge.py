    def create(self, trans, payload={}, **kwd):
        if not payload:
            payload = kwd
        message = trans.check_csrf_token(payload)
        if message:
            return self.message_exception(trans, message)
        user, message = self.user_manager.register(trans, **_filtered_registration_params_dict(payload))
        if message:
            return self.message_exception(trans, message, sanitize=False)
        elif user and not trans.user_is_admin:
            trans.handle_user_login(user)
            trans.log_event("User created a new account")
            trans.log_event("User logged in")
        return {"message": "Success."}