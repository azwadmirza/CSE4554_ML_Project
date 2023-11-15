    def write_script(self, script_name, contents, mode="t", *ignored):
        """Write an executable file to the scripts directory"""
        if "__PEX_UNVENDORED__" in __import__("os").environ:
          from setuptools.command.easy_install import chmod, current_umask  # vendor:skip
        else:
          from pex.third_party.setuptools.command.easy_install import chmod, current_umask


        log.info("Installing %s script to %s", script_name, self.install_dir)
        target = os.path.join(self.install_dir, script_name)
        self.outfiles.append(target)

        mask = current_umask()
        if not self.dry_run:
            ensure_directory(target)
            f = open(target, "w" + mode)
            f.write(contents)
            f.close()
            chmod(target, 0o777 - mask)