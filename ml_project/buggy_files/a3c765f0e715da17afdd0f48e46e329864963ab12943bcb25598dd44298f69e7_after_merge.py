    def assertonly(self):

        self.cert = crypto_utils.load_certificate(self.path)

        def _validate_signature_algorithms():
            if self.signature_algorithms:
                if self.cert.get_signature_algorithm() not in self.signature_algorithms:
                    self.message.append(
                        'Invalid signature algorithm (got %s, expected one of %s)' % (self.cert.get_signature_algorithm(), self.signature_algorithms)
                    )

        def _validate_subject():
            if self.subject:
                expected_subject = [(OpenSSL._util.lib.OBJ_txt2nid(sub[0]), sub[1]) for sub in self.subject]
                cert_subject = self.cert.get_subject().get_components()
                current_subject = [(OpenSSL._util.lib.OBJ_txt2nid(sub[0]), sub[1]) for sub in cert_subject]
                if (not self.subject_strict and not all(x in current_subject for x in expected_subject)) or \
                   (self.subject_strict and not set(expected_subject) == set(current_subject)):
                    self.message.append(
                        'Invalid subject component (got %s, expected all of %s to be present)' % (cert_subject, self.subject)
                    )

        def _validate_issuer():
            if self.issuer:
                expected_issuer = [(OpenSSL._util.lib.OBJ_txt2nid(iss[0]), iss[1]) for iss in self.issuer]
                cert_issuer = self.cert.get_issuer().get_components()
                current_issuer = [(OpenSSL._util.lib.OBJ_txt2nid(iss[0]), iss[1]) for iss in cert_issuer]
                if (not self.issuer_strict and not all(x in current_issuer for x in expected_issuer)) or \
                   (self.issuer_strict and not set(expected_issuer) == set(current_issuer)):
                    self.message.append(
                        'Invalid issuer component (got %s, expected all of %s to be present)' % (cert_issuer, self.issuer)
                    )

        def _validate_has_expired():
            if self.has_expired:
                if self.has_expired != self.cert.has_expired():
                    self.message.append(
                        'Certificate expiration check failed (certificate expiration is %s, expected %s)' % (self.cert.has_expired(), self.has_expired)
                    )

        def _validate_version():
            if self.version:
                # Version numbers in certs are off by one:
                # v1: 0, v2: 1, v3: 2 ...
                if self.version != self.cert.get_version() + 1:
                    self.message.append(
                        'Invalid certificate version number (got %s, expected %s)' % (self.cert.get_version() + 1, self.version)
                    )

        def _validate_keyUsage():
            if self.keyUsage:
                for extension_idx in range(0, self.cert.get_extension_count()):
                    extension = self.cert.get_extension(extension_idx)
                    if extension.get_short_name() == b'keyUsage':
                        keyUsage = [OpenSSL._util.lib.OBJ_txt2nid(keyUsage) for keyUsage in self.keyUsage]
                        current_ku = [OpenSSL._util.lib.OBJ_txt2nid(usage.strip()) for usage in
                                      to_bytes(extension, errors='surrogate_or_strict').split(b',')]
                        if (not self.keyUsage_strict and not all(x in current_ku for x in keyUsage)) or \
                           (self.keyUsage_strict and not set(keyUsage) == set(current_ku)):
                            self.message.append(
                                'Invalid keyUsage component (got %s, expected all of %s to be present)' % (str(extension).split(', '), self.keyUsage)
                            )

        def _validate_extendedKeyUsage():
            if self.extendedKeyUsage:
                for extension_idx in range(0, self.cert.get_extension_count()):
                    extension = self.cert.get_extension(extension_idx)
                    if extension.get_short_name() == b'extendedKeyUsage':
                        extKeyUsage = [OpenSSL._util.lib.OBJ_txt2nid(keyUsage) for keyUsage in self.extendedKeyUsage]
                        current_xku = [OpenSSL._util.lib.OBJ_txt2nid(usage.strip()) for usage in
                                       to_bytes(extension, errors='surrogate_or_strict').split(b',')]
                        if (not self.extendedKeyUsage_strict and not all(x in current_xku for x in extKeyUsage)) or \
                           (self.extendedKeyUsage_strict and not set(extKeyUsage) == set(current_xku)):
                            self.message.append(
                                'Invalid extendedKeyUsage component (got %s, expected all of %s to be present)' % (str(extension).split(', '),
                                                                                                                   self.extendedKeyUsage)
                            )

        def _validate_subjectAltName():
            if self.subjectAltName:
                for extension_idx in range(0, self.cert.get_extension_count()):
                    extension = self.cert.get_extension(extension_idx)
                    if extension.get_short_name() == b'subjectAltName':
                        l_altnames = [altname.replace(b'IP Address', b'IP') for altname in
                                      to_bytes(extension, errors='surrogate_or_strict').split(b', ')]
                        if (not self.subjectAltName_strict and not all(x in l_altnames for x in self.subjectAltName)) or \
                           (self.subjectAltName_strict and not set(self.subjectAltName) == set(l_altnames)):
                            self.message.append(
                                'Invalid subjectAltName component (got %s, expected all of %s to be present)' % (l_altnames, self.subjectAltName)
                            )

        def _validate_notBefore():
            if self.notBefore:
                if self.cert.get_notBefore() != self.notBefore:
                    self.message.append(
                        'Invalid notBefore component (got %s, expected %s to be present)' % (self.cert.get_notBefore(), self.notBefore)
                    )

        def _validate_notAfter():
            if self.notAfter:
                if self.cert.get_notAfter() != self.notAfter:
                    self.message.append(
                        'Invalid notAfter component (got %s, expected %s to be present)' % (self.cert.get_notAfter(), self.notAfter)
                    )

        def _validate_valid_at():
            if self.valid_at:
                if not (self.cert.get_notBefore() <= self.valid_at <= self.cert.get_notAfter()):
                    self.message.append(
                        'Certificate is not valid for the specified date (%s) - notBefore: %s - notAfter: %s' % (self.valid_at,
                                                                                                                 self.cert.get_notBefore(),
                                                                                                                 self.cert.get_notAfter())
                    )

        def _validate_invalid_at():
            if self.invalid_at:
                if not (self.invalid_at <= self.cert.get_notBefore() or self.invalid_at >= self.cert.get_notAfter()):
                    self.message.append(
                        'Certificate is not invalid for the specified date (%s) - notBefore: %s - notAfter: %s' % (self.invalid_at,
                                                                                                                   self.cert.get_notBefore(),
                                                                                                                   self.cert.get_notAfter())
                    )

        def _validate_valid_in():
            if self.valid_in:
                valid_in_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.valid_in)
                valid_in_date = to_bytes(valid_in_date.strftime('%Y%m%d%H%M%SZ'), errors='surrogate_or_strict')
                if not (self.cert.get_notBefore() <= valid_in_date <= self.cert.get_notAfter()):
                    self.message.append(
                        'Certificate is not valid in %s seconds from now (%s) - notBefore: %s - notAfter: %s' % (self.valid_in,
                                                                                                                 valid_in_date,
                                                                                                                 self.cert.get_notBefore(),
                                                                                                                 self.cert.get_notAfter())
                    )

        for validation in ['signature_algorithms', 'subject', 'issuer',
                           'has_expired', 'version', 'keyUsage',
                           'extendedKeyUsage', 'subjectAltName',
                           'notBefore', 'notAfter', 'valid_at',
                           'invalid_at', 'valid_in']:
            f_name = locals()['_validate_%s' % validation]
            f_name()