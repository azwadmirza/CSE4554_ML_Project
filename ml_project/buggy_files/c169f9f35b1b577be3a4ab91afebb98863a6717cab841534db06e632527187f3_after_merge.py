    def _generate_csr(self):
        req = crypto.X509Req()
        req.set_version(self.version - 1)
        subject = req.get_subject()
        for entry in self.subject:
            if entry[1] is not None:
                # Workaround for https://github.com/pyca/pyopenssl/issues/165
                nid = OpenSSL._util.lib.OBJ_txt2nid(to_bytes(entry[0]))
                OpenSSL._util.lib.X509_NAME_add_entry_by_NID(subject._name, nid, OpenSSL._util.lib.MBSTRING_UTF8, to_bytes(entry[1]), -1, -1, 0)

        extensions = []
        if self.subjectAltName:
            altnames = ', '.join(self.subjectAltName)
            try:
                extensions.append(crypto.X509Extension(b"subjectAltName", self.subjectAltName_critical, altnames.encode('ascii')))
            except OpenSSL.crypto.Error as e:
                raise CertificateSigningRequestError(
                    'Error while parsing Subject Alternative Names {0} (check for missing type prefix, such as "DNS:"!): {1}'.format(
                        ', '.join(["{0}".format(san) for san in self.subjectAltName]), str(e)
                    )
                )

        if self.keyUsage:
            usages = ', '.join(self.keyUsage)
            extensions.append(crypto.X509Extension(b"keyUsage", self.keyUsage_critical, usages.encode('ascii')))

        if self.extendedKeyUsage:
            usages = ', '.join(self.extendedKeyUsage)
            extensions.append(crypto.X509Extension(b"extendedKeyUsage", self.extendedKeyUsage_critical, usages.encode('ascii')))

        if self.basicConstraints:
            usages = ', '.join(self.basicConstraints)
            extensions.append(crypto.X509Extension(b"basicConstraints", self.basicConstraints_critical, usages.encode('ascii')))

        if self.ocspMustStaple:
            extensions.append(crypto.X509Extension(OPENSSL_MUST_STAPLE_NAME, self.ocspMustStaple_critical, OPENSSL_MUST_STAPLE_VALUE))

        if extensions:
            req.add_extensions(extensions)

        req.set_pubkey(self.privatekey)
        req.sign(self.privatekey, self.digest)
        self.request = req

        return crypto.dump_certificate_request(crypto.FILETYPE_PEM, self.request)