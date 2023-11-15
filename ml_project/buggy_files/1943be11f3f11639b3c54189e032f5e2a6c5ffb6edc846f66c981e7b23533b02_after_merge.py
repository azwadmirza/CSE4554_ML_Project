    def get_mgmt_svc_client(self, client_type, base_url=None, api_version=None):
        self.log('Getting management service client {0}'.format(client_type.__name__))
        self.check_client_version(client_type)
        if api_version:
            client = client_type(self.azure_credentials,
                                 self.subscription_id,
                                 api_version=api_version,
                                 base_url=base_url)
        else:
            client = client_type(self.azure_credentials,
                                 self.subscription_id,
                                 base_url=base_url)

        # Add user agent for Ansible
        client.config.add_user_agent(ANSIBLE_USER_AGENT)
        # Add user agent when running from Cloud Shell
        if CLOUDSHELL_USER_AGENT_KEY in os.environ:
            client.config.add_user_agent(os.environ[CLOUDSHELL_USER_AGENT_KEY])
        # Add user agent when running from VSCode extension
        if VSCODEEXT_USER_AGENT_KEY in os.environ:
            client.config.add_user_agent(os.environ[VSCODEEXT_USER_AGENT_KEY])

        if self._cert_validation_mode == 'ignore':
            client.config.session_configuration_callback = self._validation_ignore_callback

        return client