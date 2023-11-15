    def tmpdir(self):
        # if _ansible_tmpdir was not set and we have a remote_tmp,
        # the module needs to create it and clean it up once finished.
        # otherwise we create our own module tmp dir from the system defaults
        if self._tmpdir is None:
            basedir = None

            basedir = os.path.expanduser(os.path.expandvars(self._remote_tmp))
            if not os.path.exists(basedir):
                try:
                    os.makedirs(basedir, mode=0o700)
                except (OSError, IOError) as e:
                    self.warn("Unable to use %s as temporary directory, "
                              "failing back to system: %s" % (basedir, to_native(e)))
                    basedir = None
                else:
                    self.warn("Module remote_tmp %s did not exist and was "
                              "created with a mode of 0700, this may cause"
                              " issues when running as another user. To "
                              "avoid this, create the remote_tmp dir with "
                              "the correct permissions manually" % basedir)

            basefile = "ansible-moduletmp-%s-" % time.time()
            try:
                tmpdir = tempfile.mkdtemp(prefix=basefile, dir=basedir)
            except (OSError, IOError) as e:
                self.fail_json(
                    msg="Failed to create remote module tmp path at dir %s "
                        "with prefix %s: %s" % (basedir, basefile, to_native(e))
                )
            if not self._keep_remote_files:
                atexit.register(shutil.rmtree, tmpdir)
            self._tmpdir = tmpdir

        return self._tmpdir