    def auth_user_ldap(self, username, password):
        """
            Method for authenticating user, auth LDAP style.
            depends on ldap module that is not mandatory requirement
            for F.A.B.

            :param username:
                The username
            :param password:
                The password
        """
        if username is None or username == "":
            return None
        user = self.find_user(username=username)
        if user is not None and (not user.is_active()):
            return None
        else:
            try:
                import ldap
            except:
                raise Exception("No ldap library for python.")
            try:
                if self.auth_ldap_allow_self_signed:
                    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
                con = ldap.initialize(self.auth_ldap_server)
                con.set_option(ldap.OPT_REFERRALS, 0)
                if self.auth_ldap_use_tls:
                    try:
                        con.start_tls_s()
                    except Exception:
                        log.info(LOGMSG_ERR_SEC_AUTH_LDAP_TLS.format(self.auth_ldap_server))
                        return None
                # Authenticate user
                if not self._bind_ldap(ldap, con, username, password):
                    if user:
                        self.update_user_auth_stat(user, False)
                    log.info(LOGMSG_WAR_SEC_LOGIN_FAILED.format(username))
                    return None
                # If user does not exist on the DB and not self user registration, go away
                if not user and not self.auth_user_registration:
                    return None
                # User does not exist, create one if self registration.
                elif not user and self.auth_user_registration:
                    new_user = self._search_ldap(ldap, con, username)
                    if not new_user:
                        log.warning(LOGMSG_WAR_SEC_NOLDAP_OBJ.format(username))
                        return None
                    ldap_user_info = new_user[0][1]
                    if self.auth_user_registration and user is None:
                        user = self.add_user(
                            username=username,
                            first_name=self.ldap_extract(ldap_user_info, self.auth_ldap_firstname_field, username),
                            last_name=self.ldap_extract(ldap_user_info, self.auth_ldap_lastname_field, username),
                            email=self.ldap_extract(ldap_user_info, self.auth_ldap_email_field, username + '@email.notfound'),
                            role=self.find_role(self.auth_user_registration_role)
                        )

                self.update_user_auth_stat(user)
                return user

            except ldap.LDAPError as e:
                if type(e.message) == dict and 'desc' in e.message:
                    log.error(LOGMSG_ERR_SEC_AUTH_LDAP.format(e.message['desc']))
                    return None
                else:
                    log.error(e)
                    return None