    def addfield(self, pkt, s, i):
        """
        There is a hack with the _ExtensionsField.i2len. It works only because
        we expect _ExtensionsField.i2m to return a string of the same size (if
        not of the same value) upon successive calls (e.g. through i2len here,
        then i2m when directly building the _ExtensionsField).

        XXX A proper way to do this would be to keep the extensions built from
        the i2len call here, instead of rebuilding them later on.
        """
        if i is None:
            if self.length_of is not None:
                fld, fval = pkt.getfield_and_val(self.length_of)

                tmp = pkt.tls_session.frozen
                pkt.tls_session.frozen = True
                f = fld.i2len(pkt, fval)
                pkt.tls_session.frozen = tmp

                i = self.adjust(pkt, f)
                if i == 0:  # for correct build if no ext and not explicitly 0
                    v = pkt.tls_session.tls_version
                    # With TLS 1.3, zero lengths are always explicit.
                    if v is None or v < 0x0304:
                        return s
                    else:
                        return s + struct.pack(self.fmt, i)
        return s + struct.pack(self.fmt, i)