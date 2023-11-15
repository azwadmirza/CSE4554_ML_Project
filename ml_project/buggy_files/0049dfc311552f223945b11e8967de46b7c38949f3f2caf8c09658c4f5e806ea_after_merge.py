    def parse_shadow_file(self):
        """Example AIX shadowfile data:
        nobody:
                password = *

        operator1:
                password = {ssha512}06$xxxxxxxxxxxx....
                lastupdate = 1549558094

        test1:
                password = *
                lastupdate = 1553695126

        """

        b_name = to_bytes(self.name)
        b_passwd = b''
        b_expires = b''
        if os.path.exists(self.SHADOWFILE) and os.access(self.SHADOWFILE, os.R_OK):
            with open(self.SHADOWFILE, 'rb') as bf:
                b_lines = bf.readlines()

            b_passwd_line = b''
            b_expires_line = b''
            try:
                for index, b_line in enumerate(b_lines):
                    # Get password and lastupdate lines which come after the username
                    if b_line.startswith(b'%s:' % b_name):
                        b_passwd_line = b_lines[index + 1]
                        b_expires_line = b_lines[index + 2]
                        break

                # Sanity check the lines because sometimes both are not present
                if b' = ' in b_passwd_line:
                    b_passwd = b_passwd_line.split(b' = ', 1)[-1].strip()

                if b' = ' in b_expires_line:
                    b_expires = b_expires_line.split(b' = ', 1)[-1].strip()

            except IndexError:
                self.module.fail_json(msg='Failed to parse shadow file %s' % self.SHADOWFILE)

        passwd = to_native(b_passwd)
        expires = to_native(b_expires) or -1
        return passwd, expires