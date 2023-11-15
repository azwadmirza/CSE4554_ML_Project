    def __init__(self, path, errno, **kwargs):
        kwargs.update({
            'path': path,
            'errno': errno,
        })
        if on_win:
            message = dals("""
            The current user does not have write permissions to a required path.
              path: %(path)s
            """)
        else:
            message = dals("""
            The current user does not have write permissions to a required path.
              path: %(path)s
              uid: %(uid)s
              gid: %(gid)s

            If you feel that permissions on this path are set incorrectly, you can manually
            change them by executing

              $ sudo chown %(uid)s:%(gid)s %(path)s

            In general, it's not advisable to use 'sudo conda'.
            """)
            import os
            kwargs.update({
                'uid': os.geteuid(),
                'gid': os.getegid(),
            })
        super(NotWritableError, self).__init__(message, **kwargs)