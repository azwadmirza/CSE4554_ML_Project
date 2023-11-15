    def do_uninstall(self, force=False):
        if not self.installed:
            # prefix may not exist, but DB may be inconsistent. Try to fix by
            # removing, but omit hooks.
            specs = spack.installed_db.query(self.spec, installed=True)
            if specs:
                spack.installed_db.remove(specs[0])
                tty.msg("Removed stale DB entry for %s" % self.spec.short_spec)
                return
            else:
                raise InstallError(str(self.spec) + " is not installed.")

        if not force:
            dependents = self.installed_dependents
            if dependents:
                raise PackageStillNeededError(self.spec, dependents)

        # Pre-uninstall hook runs first.
        with self._prefix_write_lock():
            spack.hooks.pre_uninstall(self)
            # Uninstalling in Spack only requires removing the prefix.
            self.remove_prefix()
            #
            spack.installed_db.remove(self.spec)
        tty.msg("Successfully uninstalled %s" % self.spec.short_spec)

        # Once everything else is done, run post install hooks
        spack.hooks.post_uninstall(self)