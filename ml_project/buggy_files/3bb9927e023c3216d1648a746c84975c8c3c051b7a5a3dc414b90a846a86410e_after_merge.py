    def md5(self, path):
        """
        Use different md5 commands depending on the OS:

         - Darwin's `md5` returns BSD-style checksums by default
         - Linux's `md5sum` needs the `--tag` flag for a similar output

         Example:
              MD5 (foo.txt) = f3d220a856b52aabbf294351e8a24300
        """
        path = shlex.quote(path)
        if self.uname == "Linux":
            md5 = self.execute("md5sum " + path).split()[0]
        elif self.uname == "Darwin":
            md5 = self.execute("md5 " + path).split()[-1]
        else:
            raise DvcException(
                f"'{self.uname}' is not supported as a SSH remote"
            )

        assert len(md5) == 32
        return md5