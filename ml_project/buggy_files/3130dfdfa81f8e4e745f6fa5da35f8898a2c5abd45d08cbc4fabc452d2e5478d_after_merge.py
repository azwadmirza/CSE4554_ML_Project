    def __init__(self, hs):
        """
        Args:
            hs (synapse.server.HomeServer): homeserver
        """
        Resource.__init__(self)

        self.hs = hs
        self.store = hs.get_datastore()
        self.registration_handler = hs.get_handlers().registration_handler

        # this is required by the request_handler wrapper
        self.clock = hs.get_clock()

        self._default_consent_version = hs.config.user_consent_version
        if self._default_consent_version is None:
            raise ConfigError(
                "Consent resource is enabled but user_consent section is "
                "missing in config file.",
            )

        consent_template_directory = hs.config.user_consent_template_dir

        loader = jinja2.FileSystemLoader(consent_template_directory)
        self._jinja_env = jinja2.Environment(
            loader=loader,
            autoescape=jinja2.select_autoescape(['html', 'htm', 'xml']),
        )

        if hs.config.form_secret is None:
            raise ConfigError(
                "Consent resource is enabled but form_secret is not set in "
                "config file. It should be set to an arbitrary secret string.",
            )

        self._hmac_secret = hs.config.form_secret.encode("utf-8")