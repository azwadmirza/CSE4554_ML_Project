    def execute_cmd(self, cmd, allow_background, encoding):
        log.verbose('Executing: %s' % cmd)
        # if PY2: cmd = cmd.encode(encoding) ?
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, close_fds=False)
        if not allow_background:
            (r, w) = (p.stdout, p.stdin)
            response = native_str_to_text(r.read(), encoding=encoding, errors='replace')
            r.close()
            w.close()
            if response:
                log.info('Stdout: %s' % response)
        return p.wait()