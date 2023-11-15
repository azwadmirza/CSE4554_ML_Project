    def __init__(
        self,
        source_credentials,
        target_principal,
        target_scopes,
        delegates=None,
        lifetime=_DEFAULT_TOKEN_LIFETIME_SECS,
    ):
        """
        Args:
            source_credentials (google.auth.Credentials): The source credential
                used as to acquire the impersonated credentials.
            target_principal (str): The service account to impersonate.
            target_scopes (Sequence[str]): Scopes to request during the
                authorization grant.
            delegates (Sequence[str]): The chained list of delegates required
                to grant the final access_token.  If set, the sequence of
                identities must have "Service Account Token Creator" capability
                granted to the prceeding identity.  For example, if set to
                [serviceAccountB, serviceAccountC], the source_credential
                must have the Token Creator role on serviceAccountB.
                serviceAccountB must have the Token Creator on
                serviceAccountC.
                Finally, C must have Token Creator on target_principal.
                If left unset, source_credential must have that role on
                target_principal.
            lifetime (int): Number of seconds the delegated credential should
                be valid for (upto 3600).
        """

        super(Credentials, self).__init__()

        self._source_credentials = copy.copy(source_credentials)
        # Service account source credentials must have the _IAM_SCOPE
        # added to refresh correctly. User credentials cannot have
        # their original scopes modified.
        if isinstance(self._source_credentials, credentials.Scoped):
            self._source_credentials = self._source_credentials.with_scopes(_IAM_SCOPE)
        self._target_principal = target_principal
        self._target_scopes = target_scopes
        self._delegates = delegates
        self._lifetime = lifetime
        self.token = None
        self.expiry = _helpers.utcnow()