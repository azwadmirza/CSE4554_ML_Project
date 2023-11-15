  def MakeCoreSdist(self):
    os.chdir(args.grr_src)
    subprocess.check_call([self.PYTHON_BIN64, "setup.py", "sdist",
                           "--dist-dir=%s" % self.BUILDDIR, "--no-make-docs",
                           "--no-make-ui-files", "--no-sync-artifacts"])
    return glob.glob(os.path.join(self.BUILDDIR,
                                  "grr-response-core-*.zip")).pop()