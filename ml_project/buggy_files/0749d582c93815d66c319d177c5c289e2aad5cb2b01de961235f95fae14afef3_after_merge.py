    def user_password(self):
        passwd = ''
        expires = ''
        if HAVE_SPWD:
            try:
                passwd = spwd.getspnam(self.name)[1]
                expires = spwd.getspnam(self.name)[7]
                return passwd, expires
            except KeyError:
                return passwd, expires
            except OSError as e:
                # Python 3.6 raises PermissionError instead of KeyError
                # Due to absence of PermissionError in python2.7 need to check
                # errno
                if e.errno in (errno.EACCES, errno.EPERM):
                    return passwd, expires
                raise

        if not self.user_exists():
            return passwd, expires
        elif self.SHADOWFILE:
            passwd, expires = self.parse_shadow_file()

        return passwd, expires