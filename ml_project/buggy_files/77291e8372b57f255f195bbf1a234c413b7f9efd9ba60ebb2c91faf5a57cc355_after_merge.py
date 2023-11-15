    def check_startup_dir(self):
        if not os.path.isdir(self.startup_dir):
            os.mkdir(self.startup_dir)
        readme = os.path.join(self.startup_dir, 'README')
        src = os.path.join(get_ipython_package_dir(), u'config', u'profile', u'README_STARTUP')

        if not os.path.exists(src):
            self.log.warn("Could not copy README_STARTUP to startup dir. Source file %s does not exist." % src)

        if os.path.exists(src) and not os.path.exists(readme):
            shutil.copy(src, readme)