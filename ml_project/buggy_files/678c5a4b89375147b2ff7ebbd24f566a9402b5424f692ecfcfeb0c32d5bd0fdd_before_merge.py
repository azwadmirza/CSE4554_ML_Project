    def _check_csr(self):
        def _check_subject(csr):
            subject = [(crypto_utils.cryptography_name_to_oid(entry[0]), entry[1]) for entry in self.subject]
            current_subject = [(sub.oid, sub.value) for sub in csr.subject]
            return set(subject) == set(current_subject)

        def _find_extension(extensions, type):
            return next(
                (ext for ext in extensions if isinstance(ext.value, type)),
                None
            )

        def _check_subjectAltName(extensions):
            current_altnames_ext = _find_extension(extensions, cryptography.x509.SubjectAlternativeName)
            current_altnames = [str(altname) for altname in current_altnames_ext.value] if current_altnames_ext else []
            altnames = [str(crypto_utils.cryptography_get_name(altname)) for altname in self.subjectAltName] if self.subjectAltName else []
            if set(altnames) != set(current_altnames):
                return False
            if altnames:
                if current_altnames_ext.critical != self.subjectAltName_critical:
                    return False
            return True

        def _check_keyUsage(extensions):
            current_keyusage_ext = _find_extension(extensions, cryptography.x509.KeyUsage)
            if not self.keyUsage:
                return current_keyusage_ext is None
            elif current_keyusage_ext is None:
                return False
            params = crypto_utils.cryptography_parse_key_usage_params(self.keyUsage)
            for param in params:
                if getattr(current_keyusage_ext.value, '_' + param) != params[param]:
                    return False
            if current_keyusage_ext.critical != self.keyUsage_critical:
                return False
            return True

        def _check_extenededKeyUsage(extensions):
            current_usages_ext = _find_extension(extensions, cryptography.x509.ExtendedKeyUsage)
            current_usages = [str(usage) for usage in current_usages_ext.value] if current_usages_ext else []
            usages = [str(crypto_utils.cryptography_name_to_oid(usage)) for usage in self.extendedKeyUsage] if self.extendedKeyUsage else []
            if set(current_usages) != set(usages):
                return False
            if usages:
                if current_usages_ext.critical != self.extendedKeyUsage_critical:
                    return False
            return True

        def _check_basicConstraints(extensions):
            bc_ext = _find_extension(extensions, cryptography.x509.BasicConstraints)
            current_ca = bc_ext.ca if bc_ext else False
            current_path_length = bc_ext.path_length if bc_ext else None
            ca, path_length = crypto_utils.cryptography_get_basic_constraints(self.basicConstraints)
            # Check CA flag
            if ca != current_ca:
                return False
            # Check path length
            if path_length != current_path_length:
                return False
            # Check criticality
            if self.basicConstraints:
                if bc_ext.critical != self.basicConstraints_critical:
                    return False
            return True

        def _check_ocspMustStaple(extensions):
            try:
                # This only works with cryptography >= 2.1
                tlsfeature_ext = _find_extension(extensions, cryptography.x509.TLSFeature)
                has_tlsfeature = True
            except AttributeError as dummy:
                tlsfeature_ext = next(
                    (ext for ext in extensions if ext.value.oid == CRYPTOGRAPHY_MUST_STAPLE_NAME),
                    None
                )
                has_tlsfeature = False
            if self.ocspMustStaple:
                if not tlsfeature_ext or tlsfeature_ext.critical != self.ocspMustStaple_critical:
                    return False
                if has_tlsfeature:
                    return cryptography.x509.TLSFeatureType.status_request in tlsfeature_ext.value
                else:
                    return tlsfeature_ext.value.value == CRYPTOGRAPHY_MUST_STAPLE_VALUE
            else:
                return tlsfeature_ext is None

        def _check_extensions(csr):
            extensions = csr.extensions
            return (_check_subjectAltName(extensions) and _check_keyUsage(extensions) and
                    _check_extenededKeyUsage(extensions) and _check_basicConstraints(extensions) and
                    _check_ocspMustStaple(extensions))

        def _check_signature(csr):
            if not csr.is_signature_valid:
                return False
            # To check whether public key of CSR belongs to private key,
            # encode both public keys and compare PEMs.
            key_a = csr.public_key().public_bytes(
                cryptography.hazmat.primitives.serialization.Encoding.PEM,
                cryptography.hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo
            )
            key_b = self.privatekey.public_key().public_bytes(
                cryptography.hazmat.primitives.serialization.Encoding.PEM,
                cryptography.hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return key_a == key_b

        try:
            csr = crypto_utils.load_certificate_request(self.path, backend='cryptography')
        except Exception as dummy:
            return False

        return _check_subject(csr) and _check_extensions(csr) and _check_signature(csr)