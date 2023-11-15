    def _auth(self, load):
        '''
        Authenticate the client, use the sent public key to encrypt the AES key
        which was generated at start up.

        This method fires an event over the master event manager. The event is
        tagged "auth" and returns a dict with information about the auth
        event

        # Verify that the key we are receiving matches the stored key
        # Store the key if it is not there
        # Make an RSA key with the pub key
        # Encrypt the AES key as an encrypted salt.payload
        # Package the return and return it
        '''

        if not salt.utils.verify.valid_id(self.opts, load['id']):
            log.info('Authentication request from invalid id %s', load['id'])
            return {'enc': 'clear',
                    'load': {'ret': False}}
        log.info('Authentication request from %s', load['id'])

        # 0 is default which should be 'unlimited'
        if self.opts['max_minions'] > 0:
            # use the ConCache if enabled, else use the minion utils
            if self.cache_cli:
                minions = self.cache_cli.get_cached()
            else:
                minions = self.ckminions.connected_ids()
                if len(minions) > 1000:
                    log.info('With large numbers of minions it is advised '
                             'to enable the ConCache with \'con_cache: True\' '
                             'in the masters configuration file.')

            if not len(minions) <= self.opts['max_minions']:
                # we reject new minions, minions that are already
                # connected must be allowed for the mine, highstate, etc.
                if load['id'] not in minions:
                    msg = ('Too many minions connected (max_minions={0}). '
                           'Rejecting connection from id '
                           '{1}'.format(self.opts['max_minions'],
                                        load['id']))
                    log.info(msg)
                    eload = {'result': False,
                             'act': 'full',
                             'id': load['id'],
                             'pub': load['pub']}

                    if self.opts.get('auth_events') is True:
                        self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
                    return {'enc': 'clear',
                            'load': {'ret': 'full'}}

        # Check if key is configured to be auto-rejected/signed
        auto_reject = self.auto_key.check_autoreject(load['id'])
        auto_sign = self.auto_key.check_autosign(load['id'], load.get(u'autosign_grains', None))

        pubfn = os.path.join(self.opts['pki_dir'],
                             'minions',
                             load['id'])
        pubfn_pend = os.path.join(self.opts['pki_dir'],
                                  'minions_pre',
                                  load['id'])
        pubfn_rejected = os.path.join(self.opts['pki_dir'],
                                      'minions_rejected',
                                      load['id'])
        pubfn_denied = os.path.join(self.opts['pki_dir'],
                                    'minions_denied',
                                    load['id'])
        if self.opts['open_mode']:
            # open mode is turned on, nuts to checks and overwrite whatever
            # is there
            pass
        elif os.path.isfile(pubfn_rejected):
            # The key has been rejected, don't place it in pending
            log.info('Public key rejected for %s. Key is present in '
                     'rejection key dir.', load['id'])
            eload = {'result': False,
                     'id': load['id'],
                     'pub': load['pub']}
            if self.opts.get('auth_events') is True:
                self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
            return {'enc': 'clear',
                    'load': {'ret': False}}

        elif os.path.isfile(pubfn):
            # The key has been accepted, check it
            with salt.utils.files.fopen(pubfn, 'r') as pubfn_handle:
                if pubfn_handle.read().strip() != load['pub'].strip():
                    log.error(
                        'Authentication attempt from %s failed, the public '
                        'keys did not match. This may be an attempt to compromise '
                        'the Salt cluster.', load['id']
                    )
                    # put denied minion key into minions_denied
                    with salt.utils.files.fopen(pubfn_denied, 'w+') as fp_:
                        fp_.write(load['pub'])
                    eload = {'result': False,
                             'id': load['id'],
                             'act': 'denied',
                             'pub': load['pub']}
                    if self.opts.get('auth_events') is True:
                        self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
                    return {'enc': 'clear',
                            'load': {'ret': False}}

        elif not os.path.isfile(pubfn_pend):
            # The key has not been accepted, this is a new minion
            if os.path.isdir(pubfn_pend):
                # The key path is a directory, error out
                log.info('New public key %s is a directory', load['id'])
                eload = {'result': False,
                         'id': load['id'],
                         'pub': load['pub']}
                if self.opts.get('auth_events') is True:
                    self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
                return {'enc': 'clear',
                        'load': {'ret': False}}

            if auto_reject:
                key_path = pubfn_rejected
                log.info('New public key for %s rejected via autoreject_file', load['id'])
                key_act = 'reject'
                key_result = False
            elif not auto_sign:
                key_path = pubfn_pend
                log.info('New public key for %s placed in pending', load['id'])
                key_act = 'pend'
                key_result = True
            else:
                # The key is being automatically accepted, don't do anything
                # here and let the auto accept logic below handle it.
                key_path = None

            if key_path is not None:
                # Write the key to the appropriate location
                with salt.utils.files.fopen(key_path, 'w+') as fp_:
                    fp_.write(load['pub'])
                ret = {'enc': 'clear',
                       'load': {'ret': key_result}}
                eload = {'result': key_result,
                         'act': key_act,
                         'id': load['id'],
                         'pub': load['pub']}
                if self.opts.get('auth_events') is True:
                    self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
                return ret

        elif os.path.isfile(pubfn_pend):
            # This key is in the pending dir and is awaiting acceptance
            if auto_reject:
                # We don't care if the keys match, this minion is being
                # auto-rejected. Move the key file from the pending dir to the
                # rejected dir.
                try:
                    shutil.move(pubfn_pend, pubfn_rejected)
                except (IOError, OSError):
                    pass
                log.info('Pending public key for %s rejected via '
                         'autoreject_file', load['id'])
                ret = {'enc': 'clear',
                       'load': {'ret': False}}
                eload = {'result': False,
                         'act': 'reject',
                         'id': load['id'],
                         'pub': load['pub']}
                if self.opts.get('auth_events') is True:
                    self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
                return ret

            elif not auto_sign:
                # This key is in the pending dir and is not being auto-signed.
                # Check if the keys are the same and error out if this is the
                # case. Otherwise log the fact that the minion is still
                # pending.
                with salt.utils.files.fopen(pubfn_pend, 'r') as pubfn_handle:
                    if pubfn_handle.read() != load['pub']:
                        log.error(
                            'Authentication attempt from %s failed, the public '
                            'key in pending did not match. This may be an '
                            'attempt to compromise the Salt cluster.', load['id']
                        )
                        # put denied minion key into minions_denied
                        with salt.utils.files.fopen(pubfn_denied, 'w+') as fp_:
                            fp_.write(load['pub'])
                        eload = {'result': False,
                                 'id': load['id'],
                                 'act': 'denied',
                                 'pub': load['pub']}
                        if self.opts.get('auth_events') is True:
                            self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
                        return {'enc': 'clear',
                                'load': {'ret': False}}
                    else:
                        log.info(
                            'Authentication failed from host %s, the key is in '
                            'pending and needs to be accepted with salt-key '
                            '-a %s', load['id'], load['id']
                        )
                        eload = {'result': True,
                                 'act': 'pend',
                                 'id': load['id'],
                                 'pub': load['pub']}
                        if self.opts.get('auth_events') is True:
                            self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
                        return {'enc': 'clear',
                                'load': {'ret': True}}
            else:
                # This key is in pending and has been configured to be
                # auto-signed. Check to see if it is the same key, and if
                # so, pass on doing anything here, and let it get automatically
                # accepted below.
                with salt.utils.files.fopen(pubfn_pend, 'r') as pubfn_handle:
                    if pubfn_handle.read() != load['pub']:
                        log.error(
                            'Authentication attempt from %s failed, the public '
                            'keys in pending did not match. This may be an '
                            'attempt to compromise the Salt cluster.', load['id']
                        )
                        # put denied minion key into minions_denied
                        with salt.utils.files.fopen(pubfn_denied, 'w+') as fp_:
                            fp_.write(load['pub'])
                        eload = {'result': False,
                                 'id': load['id'],
                                 'pub': load['pub']}
                        if self.opts.get('auth_events') is True:
                            self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
                        return {'enc': 'clear',
                                'load': {'ret': False}}
                    else:
                        os.remove(pubfn_pend)

        else:
            # Something happened that I have not accounted for, FAIL!
            log.warning('Unaccounted for authentication failure')
            eload = {'result': False,
                     'id': load['id'],
                     'pub': load['pub']}
            if self.opts.get('auth_events') is True:
                self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
            return {'enc': 'clear',
                    'load': {'ret': False}}

        log.info('Authentication accepted from %s', load['id'])
        # only write to disk if you are adding the file, and in open mode,
        # which implies we accept any key from a minion.
        if not os.path.isfile(pubfn) and not self.opts['open_mode']:
            with salt.utils.files.fopen(pubfn, 'w+') as fp_:
                fp_.write(load['pub'])
        elif self.opts['open_mode']:
            disk_key = ''
            if os.path.isfile(pubfn):
                with salt.utils.files.fopen(pubfn, 'r') as fp_:
                    disk_key = fp_.read()
            if load['pub'] and load['pub'] != disk_key:
                log.debug('Host key change detected in open mode.')
                with salt.utils.files.fopen(pubfn, 'w+') as fp_:
                    fp_.write(load['pub'])

        pub = None

        # the con_cache is enabled, send the minion id to the cache
        if self.cache_cli:
            self.cache_cli.put_cache([load['id']])

        # The key payload may sometimes be corrupt when using auto-accept
        # and an empty request comes in
        try:
            pub = salt.crypt.get_rsa_pub_key(pubfn)
        except (ValueError, IndexError, TypeError) as err:
            log.error('Corrupt public key "%s": %s', pubfn, err)
            return {'enc': 'clear',
                    'load': {'ret': False}}

        if not HAS_M2:
            cipher = PKCS1_OAEP.new(pub)
        ret = {'enc': 'pub',
               'pub_key': self.master_key.get_pub_str(),
               'publish_port': self.opts['publish_port']}

        # sign the master's pubkey (if enabled) before it is
        # sent to the minion that was just authenticated
        if self.opts['master_sign_pubkey']:
            # append the pre-computed signature to the auth-reply
            if self.master_key.pubkey_signature():
                log.debug('Adding pubkey signature to auth-reply')
                log.debug(self.master_key.pubkey_signature())
                ret.update({'pub_sig': self.master_key.pubkey_signature()})
            else:
                # the master has its own signing-keypair, compute the master.pub's
                # signature and append that to the auth-reply

                # get the key_pass for the signing key
                key_pass = salt.utils.sdb.sdb_get(self.opts['signing_key_pass'], self.opts)

                log.debug("Signing master public key before sending")
                pub_sign = salt.crypt.sign_message(self.master_key.get_sign_paths()[1],
                                                   ret['pub_key'], key_pass)
                ret.update({'pub_sig': binascii.b2a_base64(pub_sign)})

        if not HAS_M2:
            mcipher = PKCS1_OAEP.new(self.master_key.key)
        if self.opts['auth_mode'] >= 2:
            if 'token' in load:
                try:
                    if HAS_M2:
                        mtoken = self.master_key.key.private_decrypt(six.b(load['token']),
                                                                     RSA.pkcs1_oaep_padding)
                    else:
                        mtoken = mcipher.decrypt(load['token'])
                    aes = '{0}_|-{1}'.format(salt.master.SMaster.secrets['aes']['secret'].value, mtoken)
                except Exception:
                    # Token failed to decrypt, send back the salty bacon to
                    # support older minions
                    pass
            else:
                aes = salt.master.SMaster.secrets['aes']['secret'].value

            if HAS_M2:
                ret['aes'] = pub.public_encrypt(six.b(aes), RSA.pkcs1_oaep_padding)
            else:
                ret['aes'] = cipher.encrypt(aes)
        else:
            if 'token' in load:
                try:
                    if HAS_M2:
                        mtoken = self.master_key.key.private_decrypt(six.b(load['token']),
                                                                     RSA.pkcs1_oaep_padding)
                        ret['token'] = pub.public_encrypt(six.b(mtoken), RSA.pkcs1_oaep_padding)
                    else:
                        mtoken = mcipher.decrypt(load['token'])
                        ret['token'] = cipher.encrypt(mtoken)
                except Exception:
                    # Token failed to decrypt, send back the salty bacon to
                    # support older minions
                    pass

            aes = salt.master.SMaster.secrets['aes']['secret'].value
            if HAS_M2:
                ret['aes'] = pub.public_encrypt(six.b(aes), RSA.pkcs1_oaep_padding)
            else:
                ret['aes'] = cipher.encrypt(aes)
        # Be aggressive about the signature
        digest = hashlib.sha256(aes).hexdigest()
        ret['sig'] = salt.crypt.private_encrypt(self.master_key.key, digest)
        eload = {'result': True,
                 'act': 'accept',
                 'id': load['id'],
                 'pub': load['pub']}
        if self.opts.get('auth_events') is True:
            self.event.fire_event(eload, salt.utils.event.tagify(prefix='auth'))
        return ret