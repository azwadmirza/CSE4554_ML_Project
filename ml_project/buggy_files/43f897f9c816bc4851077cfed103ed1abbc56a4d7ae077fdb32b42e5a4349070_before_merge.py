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