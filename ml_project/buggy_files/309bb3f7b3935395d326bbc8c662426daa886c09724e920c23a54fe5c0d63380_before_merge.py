    def __init__(self, module):
        self.module = module

        if module.params['zone'] is None:
            if module.params['record'][-1] != '.':
                self.module.fail_json(msg='record must be absolute when omitting zone parameter')
            self.zone = self.lookup_zone()
        else:
            self.zone = module.params['zone']

            if self.zone[-1] != '.':
                self.zone += '.'

        if module.params['record'][-1] != '.':
            self.fqdn = module.params['record'] + '.' + self.zone
        else:
            self.fqdn = module.params['record']

        if module.params['key_name']:
            try:
                self.keyring = dns.tsigkeyring.from_text({
                    module.params['key_name']: module.params['key_secret']
                })
            except TypeError:
                module.fail_json(msg='Missing key_secret')
            except binascii_error as e:
                module.fail_json(msg='TSIG key error: %s' % to_native(e))
        else:
            self.keyring = None

        if module.params['key_algorithm'] == 'hmac-md5':
            self.algorithm = 'HMAC-MD5.SIG-ALG.REG.INT'
        else:
            self.algorithm = module.params['key_algorithm']

        if self.module.params['type'].lower() == 'txt':
            self.value = list(map(self.txt_helper, self.module.params['value']))
        else:
            self.value = self.module.params['value']

        self.dns_rc = 0