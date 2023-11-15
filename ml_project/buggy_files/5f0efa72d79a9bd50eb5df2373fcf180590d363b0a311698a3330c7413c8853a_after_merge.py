    def execute_cmd(self, cmd, allow_background, encoding):
        log.verbose('Executing: %s', cmd)
        p = subprocess.Popen(text_to_native_str(cmd, encoding=io_encoding), shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=False)
        if not allow_background:
            r, w = (p.stdout, p.stdin)
            response = r.read().decode(io_encoding)
            r.close()
            w.close()
            if response:
                log.info('Stdout: %s', response.rstrip())  # rstrip to get rid of newlines
        return p.wait()