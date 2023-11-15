    def cmd_output_p(
            *cmd: str,
            retcode: Optional[int] = 0,
            **kwargs: Any,
    ) -> Tuple[int, bytes, Optional[bytes]]:
        assert retcode is None
        assert kwargs['stderr'] == subprocess.STDOUT, kwargs['stderr']
        _setdefault_kwargs(kwargs)

        try:
            cmd = parse_shebang.normalize_cmd(cmd)
        except parse_shebang.ExecutableNotFoundError as e:
            return e.to_output()

        with open(os.devnull) as devnull, Pty() as pty:
            assert pty.r is not None
            kwargs.update({'stdin': devnull, 'stdout': pty.w, 'stderr': pty.w})
            proc = subprocess.Popen(cmd, **kwargs)
            pty.close_w()

            buf = b''
            while True:
                try:
                    bts = os.read(pty.r, 4096)
                except OSError as e:
                    if e.errno == errno.EIO:
                        bts = b''
                    else:
                        raise
                else:
                    buf += bts
                if not bts:
                    break

        return proc.wait(), buf, None