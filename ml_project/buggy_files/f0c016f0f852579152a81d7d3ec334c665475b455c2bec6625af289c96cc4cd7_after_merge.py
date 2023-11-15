    def popen(self, args, cwd=None, env=None, redirect=True, returnout=False, ignore_ret=False):
        stdout = outpath = None
        resultjson = self.session.config.option.resultjson
        if resultjson or redirect:
            fout = self._initlogpath(self.id)
            fout.write("actionid: %s\nmsg: %s\ncmdargs: %r\n\n" % (self.id, self.msg, args))
            fout.flush()
            outpath = py.path.local(fout.name)
            fin = outpath.open('rb')
            fin.read()  # read the header, so it won't be written to stdout
            stdout = fout
        elif returnout:
            stdout = subprocess.PIPE
        if cwd is None:
            # XXX cwd = self.session.config.cwd
            cwd = py.path.local()
        try:
            popen = self._popen(args, cwd, env=env,
                                stdout=stdout, stderr=subprocess.STDOUT)
        except OSError as e:
            self.report.error("invocation failed (errno %d), args: %s, cwd: %s" %
                              (e.errno, args, cwd))
            raise
        popen.outpath = outpath
        popen.args = [str(x) for x in args]
        popen.cwd = cwd
        popen.action = self
        self._popenlist.append(popen)
        try:
            self.report.logpopen(popen, env=env)
            try:
                if resultjson and not redirect:
                    if popen.stderr is not None:
                        # prevent deadlock
                        raise ValueError("stderr must not be piped here")
                    # we read binary from the process and must write using a
                    # binary stream
                    buf = getattr(sys.stdout, 'buffer', sys.stdout)
                    out = None
                    last_time = time.time()
                    while 1:
                        # we have to read one byte at a time, otherwise there
                        # might be no output for a long time with slow tests
                        data = fin.read(1)
                        if data:
                            buf.write(data)
                            if b'\n' in data or (time.time() - last_time) > 1:
                                # we flush on newlines or after 1 second to
                                # provide quick enough feedback to the user
                                # when printing a dot per test
                                buf.flush()
                                last_time = time.time()
                        elif popen.poll() is not None:
                            if popen.stdout is not None:
                                popen.stdout.close()
                            break
                        else:
                            time.sleep(0.1)
                            # the seek updates internal read buffers
                            fin.seek(0, 1)
                    fin.close()
                else:
                    out, err = popen.communicate()
            except KeyboardInterrupt:
                self.report.keyboard_interrupt()
                popen.wait()
                raise
            ret = popen.wait()
        finally:
            self._popenlist.remove(popen)
        if ret and not ignore_ret:
            invoked = " ".join(map(str, popen.args))
            if outpath:
                self.report.error("invocation failed (exit code %d), logfile: %s" %
                                  (ret, outpath))
                out = outpath.read()
                self.report.error(out)
                if hasattr(self, "commandlog"):
                    self.commandlog.add_command(popen.args, out, ret)
                raise tox.exception.InvocationError(
                    "%s (see %s)" % (invoked, outpath), ret)
            else:
                raise tox.exception.InvocationError("%r" % (invoked,), ret)
        if not out and outpath:
            out = outpath.read()
        if hasattr(self, "commandlog"):
            self.commandlog.add_command(popen.args, out, ret)
        return out