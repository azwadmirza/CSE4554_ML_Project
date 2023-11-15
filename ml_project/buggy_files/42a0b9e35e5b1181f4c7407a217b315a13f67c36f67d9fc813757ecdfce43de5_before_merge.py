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

        if not self.user_exists():
            return passwd, expires
        elif self.SHADOWFILE:
            # Read shadow file for user's encrypted password string
            if os.path.exists(self.SHADOWFILE) and os.access(self.SHADOWFILE, os.R_OK):
                for line in open(self.SHADOWFILE).readlines():
                    if line.startswith('%s:' % self.name):
                        passwd = line.split(':')[1]
                        expires = line.split(':')[self.SHADOWFILE_EXPIRE_INDEX] or -1
        return passwd, expires