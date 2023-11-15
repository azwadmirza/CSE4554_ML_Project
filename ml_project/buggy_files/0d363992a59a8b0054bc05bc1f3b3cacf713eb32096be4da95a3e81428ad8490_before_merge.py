    def tmpdir(self):
        # if _ansible_tmpdir was not set, the module needs to create it and
        # clean it up once finished.
        if self._tmpdir is None:
            basedir = os.path.expanduser(os.path.expandvars(self._remote_tmp))
            if not os.path.exists(basedir):
                self.warn("Module remote_tmp %s did not exist and was created "
                          "with a mode of 0700, this may cause issues when "
                          "running as another user. To avoid this, create the "
                          "remote_tmp dir with the correct permissions "
                          "manually" % basedir)
                os.makedirs(basedir, mode=0o700)

            basefile = "ansible-moduletmp-%s-" % time.time()
            tmpdir = tempfile.mkdtemp(prefix=basefile, dir=basedir)
            if not self._keep_remote_files:
                atexit.register(shutil.rmtree, tmpdir)
            self._tmpdir = tmpdir

        return self._tmpdir