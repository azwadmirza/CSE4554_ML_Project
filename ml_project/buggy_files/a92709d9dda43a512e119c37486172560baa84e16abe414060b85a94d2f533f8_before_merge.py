    def install_mobsf_ca(self, action):
        """Install or Remove MobSF Root CA."""
        ca_construct = '{}.0'
        pem = open(get_ca_dir(), 'rb').read()
        ca_file = crypto.load_certificate(crypto.FILETYPE_PEM, pem)
        ca_file_hash = hex(ca_file.subject_name_hash()).lstrip('0x')
        ca_file = os.path.join('/system/etc/security/cacerts/',
                               ca_construct.format(ca_file_hash))
        if action == 'install':
            logger.info('Installing MobSF RootCA')
            self.adb_command(['push',
                              get_ca_dir(),
                              ca_file])
            self.adb_command(['chmod',
                              '644',
                              ca_file], True)
        elif action == 'remove':
            logger.info('Removing MobSF RootCA')
            self.adb_command(['rm',
                              ca_file], True)