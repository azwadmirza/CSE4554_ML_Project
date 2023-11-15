    def save_account(self, token, url=QE_URL, overwrite=False, **kwargs):
        """Save the account to disk for future use.

        Login into Quantum Experience or IBMQ using the provided credentials,
        adding the account to the current session. The account is stored in
        disk for future use.

        Args:
            token (str): Quantum Experience or IBM Q API token.
            url (str): URL for Quantum Experience or IBM Q (for IBM Q,
                including the hub, group and project in the URL).
            overwrite (bool): overwrite existing credentials.
            **kwargs (dict):
                * proxies (dict): Proxy configuration for the API.
                * verify (bool): If False, ignores SSL certificates errors
        """
        credentials = Credentials(token, url, **kwargs)
        store_credentials(credentials, overwrite=overwrite)