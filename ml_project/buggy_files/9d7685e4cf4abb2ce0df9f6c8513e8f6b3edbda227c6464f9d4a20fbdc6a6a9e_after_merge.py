    def get_or_create_user(self, username, ldap_user):
        # type: (str, _LDAPUser) -> Tuple[UserProfile, bool]
        try:
            user_profile = get_user_profile_by_email(username)
            if not user_profile.is_active or user_profile.realm.deactivated:
                raise ZulipLDAPException("Realm has been deactivated")
            if not ldap_auth_enabled(user_profile.realm):
                raise ZulipLDAPException("LDAP Authentication is not enabled")
            return user_profile, False
        except UserProfile.DoesNotExist:
            if self._realm is None:
                raise ZulipLDAPException("Realm is None")
            # No need to check for an inactive user since they don't exist yet
            if self._realm.deactivated:
                raise ZulipLDAPException("Realm has been deactivated")

            full_name_attr = settings.AUTH_LDAP_USER_ATTR_MAP["full_name"]
            short_name = full_name = ldap_user.attrs[full_name_attr][0]
            try:
                full_name = check_full_name(full_name)
            except JsonableError as e:
                raise ZulipLDAPException(e.error)
            if "short_name" in settings.AUTH_LDAP_USER_ATTR_MAP:
                short_name_attr = settings.AUTH_LDAP_USER_ATTR_MAP["short_name"]
                short_name = ldap_user.attrs[short_name_attr][0]

            user_profile = do_create_user(username, None, self._realm, full_name, short_name)
            return user_profile, True