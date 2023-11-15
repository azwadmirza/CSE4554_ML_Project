    def __autoregistration(self, trans, login, password):
        """
        Does the autoregistration if enabled. Returns a message
        """
        autoreg = trans.app.auth_manager.check_auto_registration(trans, login, password)
        user = None
        if autoreg["auto_reg"]:
            email = autoreg["email"]
            username = autoreg["username"]
            message = " ".join([validate_email(trans, email, allow_empty=True),
                                validate_publicname(trans, username)]).rstrip()
            if not message:
                user = self.user_manager.create(email=email, username=username, password="")
                if trans.app.config.user_activation_on:
                    self.user_manager.send_activation_email(trans, email, username)
                # The handle_user_login() method has a call to the history_set_default_permissions() method
                # (needed when logging in with a history), user needs to have default permissions set before logging in
                if not trans.user_is_admin:
                    trans.handle_user_login(user)
                    trans.log_event("User (auto) created a new account")
                    trans.log_event("User logged in")
                if "attributes" in autoreg and "roles" in autoreg["attributes"]:
                    self.__handle_role_and_group_auto_creation(
                        trans, user, autoreg["attributes"]["roles"],
                        auto_create_groups=autoreg["auto_create_groups"],
                        auto_create_roles=autoreg["auto_create_roles"],
                        auto_assign_roles_to_groups_only=autoreg["auto_assign_roles_to_groups_only"])
            else:
                message = "Auto-registration failed, contact your local Galaxy administrator. %s" % message
        else:
            message = "No such user or invalid password."
        return message, user