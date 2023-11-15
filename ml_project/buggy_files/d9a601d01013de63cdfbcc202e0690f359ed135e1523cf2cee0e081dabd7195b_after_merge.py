    def _encrypt_private(self, ret, dictkey, target):
        '''
        The server equivalent of ReqChannel.crypted_transfer_decode_dictentry
        '''
        # encrypt with a specific AES key
        pubfn = os.path.join(self.opts['pki_dir'],
                             'minions',
                             target)
        key = salt.crypt.Crypticle.generate_key_string()
        pcrypt = salt.crypt.Crypticle(
            self.opts,
            key)
        try:
            with salt.utils.fopen(pubfn) as f:
                pub = RSA.importKey(f.read())
        except (ValueError, IndexError, TypeError):
            return self.crypticle.dumps({})
        except IOError:
            log.error('AES key not found')
            return 'AES key not found'

        pret = {}
        cipher = PKCS1_OAEP.new(pub)
        if six.PY2:
            pret['key'] = cipher.encrypt(key)
        else:
            pret['key'] = cipher.encrypt(salt.utils.to_bytes(key))
        pret[dictkey] = pcrypt.dumps(
            ret if ret is not False else {}
        )
        return pret