    def _load_for_exe(cls, exe):
        from virtualenv.util.subprocess import subprocess, Popen

        cmd = cls._get_exe_cmd(exe)
        # noinspection DuplicatedCode
        # this is duplicated here because this file is executed on its own, so cannot be refactored otherwise
        logging.debug(u"get interpreter info via cmd: %s", Cmd(cmd))
        try:
            process = Popen(
                cmd, universal_newlines=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )
            out, err = process.communicate()
            code = process.returncode
        except OSError as os_error:
            out, err, code = "", os_error.strerror, os_error.errno
        result, failure = None, None
        if code == 0:
            result = cls.from_json(out)
            result.executable = exe  # keep original executable as this may contain initialization code
        else:
            msg = "failed to query {} with code {}{}{}".format(
                exe, code, " out: {!r}".format(out) if out else "", " err: {!r}".format(err) if err else ""
            )
            failure = RuntimeError(msg)
        return failure, result