    def generate(self, module):

        if not os.path.exists(self.privatekey_path):
            raise CertificateError(
                'The private key %s does not exist' % self.privatekey_path
            )

        if not os.path.exists(self.csr_path):
            raise CertificateError(
                'The certificate signing request file %s does not exist' % self.csr_path
            )

        if not self.check(module, perms_required=False) or self.force:
            cert = crypto.X509()
            cert.set_serial_number(self.serial_number)
            if self.notBefore:
                cert.set_notBefore(self.notBefore)
            else:
                cert.gmtime_adj_notBefore(0)
            if self.notAfter:
                cert.set_notAfter(self.notAfter)
            else:
                # If no NotAfter specified, expire in
                # 10 years. 315360000 is 10 years in seconds.
                cert.gmtime_adj_notAfter(315360000)
            cert.set_subject(self.csr.get_subject())
            cert.set_issuer(self.csr.get_subject())
            cert.set_version(self.version - 1)
            cert.set_pubkey(self.csr.get_pubkey())
            cert.add_extensions(self.csr.get_extensions())

            cert.sign(self.privatekey, self.digest)
            self.cert = cert

            try:
                with open(self.path, 'wb') as cert_file:
                    cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, self.cert))
            except EnvironmentError as exc:
                raise CertificateError(exc)

            self.changed = True

        file_args = module.load_file_common_arguments(module.params)
        if module.set_fs_attributes_if_different(file_args, False):
            self.changed = True