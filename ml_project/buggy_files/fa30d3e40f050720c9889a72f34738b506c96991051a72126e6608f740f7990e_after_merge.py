    def installation_id(self):
        """
        Returns the installation UUID for this AWS SAM CLI installation. If the
        installation id has not yet been set, it will be set before returning.

        Examples
        --------

        >>> gc = GlobalConfig()
        >>> gc.installation_id
        "7b7d4db7-2f54-45ba-bf2f-a2cbc9e74a34"

        >>> gc = GlobalConfig()
        >>> gc.installation_id
        None

        Returns
        -------
        A string containing the installation UUID, or None in case of an error.
        """
        if self._installation_id:
            return self._installation_id
        try:
            self._installation_id = self._get_or_set_uuid(INSTALLATION_ID_KEY)
            return self._installation_id
        except (ValueError, IOError, OSError):
            return None