    def start_onion_service(self, port):
        """
        Start a onion service on port 80, pointing to the given port, and
        return the onion hostname.
        """
        self.common.log('Onion', 'start_onion_service')

        self.auth_string = None
        if not self.supports_ephemeral:
            raise TorTooOld(strings._('error_ephemeral_not_supported'))
        if self.stealth and not self.supports_stealth:
            raise TorTooOld(strings._('error_stealth_not_supported'))

        print(strings._("config_onion_service").format(int(port)))
        print(strings._('using_ephemeral'))

        if self.stealth:
            if self.settings.get('hidservauth_string'):
                hidservauth_string = self.settings.get('hidservauth_string').split()[2]
                basic_auth = {'onionshare':hidservauth_string}
            else:
                basic_auth = {'onionshare':None}
        else:
            basic_auth = None

        if self.settings.get('private_key'):
            key_content = self.settings.get('private_key')
            # is the key a v2 key?
            if onionkey.is_v2_key(key_content):
                key_type = "RSA1024"
                # The below section is commented out because re-publishing
                # a pre-prepared v3 private key is currently unstable in Tor.
                # This is fixed upstream but won't reach stable until 0.3.5
                # (expected in December 2018)
                # See https://trac.torproject.org/projects/tor/ticket/25552
                # Until then, we will deliberately not work with 'persistent'
                # v3 onions, which should not be possible via the GUI settings
                # anyway.
                # Our ticket: https://github.com/micahflee/onionshare/issues/677
                #
                # Assume it was a v3 key
                # key_type = "ED25519-V3"
            else:
                raise TorErrorProtocolError(strings._('error_invalid_private_key'))
        else:
            # Work out if we can support v3 onion services, which are preferred
            if Version(self.tor_version) >= Version('0.3.3.1') and not self.settings.get('use_legacy_v2_onions'):
                key_type = "ED25519-V3"
                key_content = onionkey.generate_v3_private_key()[0]
            else:
                # fall back to v2 onion services
                key_type = "RSA1024"
                key_content = onionkey.generate_v2_private_key()[0]

        # v3 onions don't yet support basic auth. Our ticket:
        # https://github.com/micahflee/onionshare/issues/697
        if key_type == "ED25519-V3" and not self.settings.get('use_legacy_v2_onions'):
            basic_auth = None
            self.stealth = False

        self.common.log('Onion', 'start_onion_service', 'key_type={}'.format(key_type))
        try:
            if basic_auth != None:
                res = self.c.create_ephemeral_hidden_service({ 80: port }, await_publication=True, basic_auth=basic_auth, key_type=key_type, key_content=key_content)
            else:
                # if the stem interface is older than 1.5.0, basic_auth isn't a valid keyword arg
                res = self.c.create_ephemeral_hidden_service({ 80: port }, await_publication=True, key_type=key_type, key_content=key_content)

        except ProtocolError as e:
            raise TorErrorProtocolError(strings._('error_tor_protocol_error').format(e.args[0]))

        self.service_id = res.service_id
        onion_host = self.service_id + '.onion'

        # A new private key was generated and is in the Control port response.
        if self.settings.get('save_private_key'):
            if not self.settings.get('private_key'):
                self.settings.set('private_key', key_content)

        if self.stealth:
            # Similar to the PrivateKey, the Control port only returns the ClientAuth
            # in the response if it was responsible for creating the basic_auth password
            # in the first place.
            # If we sent the basic_auth (due to a saved hidservauth_string in the settings),
            # there is no response here, so use the saved value from settings.
            if self.settings.get('save_private_key'):
                if self.settings.get('hidservauth_string'):
                    self.auth_string = self.settings.get('hidservauth_string')
                else:
                    auth_cookie = list(res.client_auth.values())[0]
                    self.auth_string = 'HidServAuth {} {}'.format(onion_host, auth_cookie)
                    self.settings.set('hidservauth_string', self.auth_string)
            else:
                auth_cookie = list(res.client_auth.values())[0]
                self.auth_string = 'HidServAuth {} {}'.format(onion_host, auth_cookie)

        if onion_host is not None:
            self.settings.save()
            return onion_host
        else:
            raise TorErrorProtocolError(strings._('error_tor_protocol_error_unknown'))