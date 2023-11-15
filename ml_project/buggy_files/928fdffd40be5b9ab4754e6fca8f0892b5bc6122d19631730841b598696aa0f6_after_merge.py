    def healthy(prefix, language_version):
        with in_env(prefix, language_version):
            retcode, _, _ = cmd_output(
                'python', '-c',
                'import ctypes, datetime, io, os, ssl, weakref',
                retcode=None,
                encoding=None,
            )
        return retcode == 0