    def ustring(self,
                indent,
                color,
                msg,
                prefix='',
                suffix='',
                endc=None):
        if endc is None:
            endc = self.ENDC

        indent *= ' '
        fmt = '{0}{1}{2}{3}{4}{5}'

        try:
            return fmt.format(
                indent,
                color,
                prefix,
                msg,
                endc,
                suffix)
        except UnicodeDecodeError:
            try:
                return fmt.format(
                    indent,
                    color,
                    prefix,
                    salt.utils.stringutils.to_unicode(msg),
                    endc,
                    suffix)
            except UnicodeDecodeError:
                # msg contains binary data that can't be decoded
                return str(fmt).format(  # future lint: disable=blacklisted-function
                    indent,
                    color,
                    prefix,
                    msg,
                    endc,
                    suffix)