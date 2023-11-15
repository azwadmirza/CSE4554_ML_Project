    def _build_winrm_kwargs(self):
        # this used to be in set_options, as win_reboot needs to be able to
        # override the conn timeout, we need to be able to build the args
        # after setting individual options. This is called by _connect before
        # starting the WinRM connection
        self._winrm_host = self.get_option('remote_addr')
        self._winrm_user = self.get_option('remote_user')
        self._winrm_pass = self._play_context.password

        self._become_method = self._play_context.become_method
        self._become_user = self._play_context.become_user
        self._become_pass = self._play_context.become_pass

        self._winrm_port = self.get_option('port')

        self._winrm_scheme = self.get_option('scheme')
        # old behaviour, scheme should default to http if not set and the port
        # is 5985 otherwise https
        if self._winrm_scheme is None:
            self._winrm_scheme = 'http' if self._winrm_port == 5985 else 'https'

        self._winrm_path = self.get_option('path')
        self._kinit_cmd = self.get_option('kerberos_command')
        self._winrm_transport = self.get_option('transport')
        self._winrm_connection_timeout = self.get_option('connection_timeout')

        if hasattr(winrm, 'FEATURE_SUPPORTED_AUTHTYPES'):
            self._winrm_supported_authtypes = set(winrm.FEATURE_SUPPORTED_AUTHTYPES)
        else:
            # for legacy versions of pywinrm, use the values we know are supported
            self._winrm_supported_authtypes = set(['plaintext', 'ssl', 'kerberos'])

        # calculate transport if needed
        if self._winrm_transport is None or self._winrm_transport[0] is None:
            # TODO: figure out what we want to do with auto-transport selection in the face of NTLM/Kerb/CredSSP/Cert/Basic
            transport_selector = ['ssl'] if self._winrm_scheme == 'https' else ['plaintext']

            if HAVE_KERBEROS and ((self._winrm_user and '@' in self._winrm_user)):
                self._winrm_transport = ['kerberos'] + transport_selector
            else:
                self._winrm_transport = transport_selector

        unsupported_transports = set(self._winrm_transport).difference(self._winrm_supported_authtypes)

        if unsupported_transports:
            raise AnsibleError('The installed version of WinRM does not support transport(s) %s' %
                               to_native(list(unsupported_transports), nonstring='simplerepr'))

        # if kerberos is among our transports and there's a password specified, we're managing the tickets
        kinit_mode = self.get_option('kerberos_mode')
        if kinit_mode is None:
            # HACK: ideally, remove multi-transport stuff
            self._kerb_managed = "kerberos" in self._winrm_transport and (self._winrm_pass is not None and self._winrm_pass != "")
        elif kinit_mode == "managed":
            self._kerb_managed = True
        elif kinit_mode == "manual":
            self._kerb_managed = False

        # arg names we're going passing directly
        internal_kwarg_mask = set(['self', 'endpoint', 'transport', 'username', 'password', 'scheme', 'path', 'kinit_mode', 'kinit_cmd'])

        self._winrm_kwargs = dict(username=self._winrm_user, password=self._winrm_pass)
        argspec = inspect.getargspec(Protocol.__init__)
        supported_winrm_args = set(argspec.args)
        supported_winrm_args.update(internal_kwarg_mask)
        passed_winrm_args = set([v.replace('ansible_winrm_', '') for v in self.get_option('_extras')])
        unsupported_args = passed_winrm_args.difference(supported_winrm_args)

        # warn for kwargs unsupported by the installed version of pywinrm
        for arg in unsupported_args:
            display.warning("ansible_winrm_{0} unsupported by pywinrm (is an up-to-date version of pywinrm installed?)".format(arg))

        # pass through matching extras, excluding the list we want to treat specially
        for arg in passed_winrm_args.difference(internal_kwarg_mask).intersection(supported_winrm_args):
            self._winrm_kwargs[arg] = self.get_option('_extras')['ansible_winrm_%s' % arg]