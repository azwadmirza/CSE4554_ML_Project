        def _check_subjectAltName(extensions):
            altnames_ext = next((ext for ext in extensions if ext.get_short_name() == b'subjectAltName'), '')
            altnames = [self._normalize_san(altname.strip()) for altname in
                        to_text(altnames_ext, errors='surrogate_or_strict').split(',') if altname.strip()]
            if self.subjectAltName:
                if (set(altnames) != set([self._normalize_san(to_text(name)) for name in self.subjectAltName]) or
                        altnames_ext.get_critical() != self.subjectAltName_critical):
                    return False
            else:
                if altnames:
                    return False

            return True