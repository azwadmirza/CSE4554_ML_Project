    def register_user(self, localpart, displayname=None, emails=[]):
        """Registers a new user with given localpart and optional displayname, emails.

        Args:
            localpart (str): The localpart of the new user.
            displayname (str|None): The displayname of the new user.
            emails (List[str]): Emails to bind to the new user.

        Raises:
            SynapseError if there is an error performing the registration. Check the
                'errcode' property for more information on the reason for failure

        Returns:
            Deferred[str]: user_id
        """
        return defer.ensureDeferred(
            self._hs.get_registration_handler().register_user(
                localpart=localpart,
                default_display_name=displayname,
                bind_emails=emails,
            )
        )