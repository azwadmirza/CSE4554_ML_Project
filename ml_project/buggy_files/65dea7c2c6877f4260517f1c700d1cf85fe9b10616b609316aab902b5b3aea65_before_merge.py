    def _check_csr(self):
        def _check_subject(csr):
            subject = [(OpenSSL._util.lib.OBJ_txt2nid(to_bytes(sub[0])), to_bytes(sub[1])) for sub in self.subject]
            current_subject = [(OpenSSL._util.lib.OBJ_txt2nid(to_bytes(sub[0])), to_bytes(sub[1])) for sub in csr.get_subject().get_components()]
            if not set(subject) == set(current_subject):
                return False

            return True

        def _check_subjectAltName(extensions):
            altnames_ext = next((ext for ext in extensions if ext.get_short_name() == b'subjectAltName'), '')
            altnames = [altname.strip() for altname in str(altnames_ext).split(',') if altname.strip()]
            # apperently openssl returns 'IP address' not 'IP' as specifier when converting the subjectAltName to string
            # although it won't accept this specifier when generating the CSR. (https://github.com/openssl/openssl/issues/4004)
            altnames = [name if not name.startswith('IP Address:') else "IP:" + name.split(':', 1)[1] for name in altnames]
            if self.subjectAltName:
                if set(altnames) != set(self.subjectAltName) or altnames_ext.get_critical() != self.subjectAltName_critical:
                    return False
            else:
                if altnames:
                    return False

            return True

        def _check_keyUsage_(extensions, extName, expected, critical):
            usages_ext = [ext for ext in extensions if ext.get_short_name() == extName]
            if (not usages_ext and expected) or (usages_ext and not expected):
                return False
            elif not usages_ext and not expected:
                return True
            else:
                current = [OpenSSL._util.lib.OBJ_txt2nid(to_bytes(usage.strip())) for usage in str(usages_ext[0]).split(',')]
                expected = [OpenSSL._util.lib.OBJ_txt2nid(to_bytes(usage)) for usage in expected]
                return set(current) == set(expected) and usages_ext[0].get_critical() == critical

        def _check_keyUsage(extensions):
            usages_ext = [ext for ext in extensions if ext.get_short_name() == b'keyUsage']
            if (not usages_ext and self.keyUsage) or (usages_ext and not self.keyUsage):
                return False
            elif not usages_ext and not self.keyUsage:
                return True
            else:
                # OpenSSL._util.lib.OBJ_txt2nid() always returns 0 for all keyUsage values
                # (since keyUsage has a fixed bitfield for these values and is not extensible).
                # Therefore, we create an extension for the wanted values, and compare the
                # data of the extensions (which is the serialized bitfield).
                expected_ext = crypto.X509Extension(b"keyUsage", False, ', '.join(self.keyUsage).encode('ascii'))
                return usages_ext[0].get_data() == expected_ext.get_data() and usages_ext[0].get_critical() == self.keyUsage_critical

        def _check_extenededKeyUsage(extensions):
            return _check_keyUsage_(extensions, b'extendedKeyUsage', self.extendedKeyUsage, self.extendedKeyUsage_critical)

        def _check_basicConstraints(extensions):
            return _check_keyUsage_(extensions, b'basicConstraints', self.basicConstraints, self.basicConstraints_critical)

        def _check_ocspMustStaple(extensions):
            oms_ext = [ext for ext in extensions if to_bytes(ext.get_short_name()) == OPENSSL_MUST_STAPLE_NAME and to_bytes(ext) == OPENSSL_MUST_STAPLE_VALUE]
            if OpenSSL.SSL.OPENSSL_VERSION_NUMBER < 0x10100000:
                # Older versions of libssl don't know about OCSP Must Staple
                oms_ext.extend([ext for ext in extensions if ext.get_short_name() == b'UNDEF' and ext.get_data() == b'\x30\x03\x02\x01\x05'])
            if self.ocspMustStaple:
                return len(oms_ext) > 0 and oms_ext[0].get_critical() == self.ocspMustStaple_critical
            else:
                return len(oms_ext) == 0

        def _check_extensions(csr):
            extensions = csr.get_extensions()
            return (_check_subjectAltName(extensions) and _check_keyUsage(extensions) and
                    _check_extenededKeyUsage(extensions) and _check_basicConstraints(extensions) and
                    _check_ocspMustStaple(extensions))

        def _check_signature(csr):
            try:
                return csr.verify(self.privatekey)
            except crypto.Error:
                return False

        try:
            csr = crypto_utils.load_certificate_request(self.path, backend='pyopenssl')
        except Exception as dummy:
            return False

        return _check_subject(csr) and _check_extensions(csr) and _check_signature(csr)