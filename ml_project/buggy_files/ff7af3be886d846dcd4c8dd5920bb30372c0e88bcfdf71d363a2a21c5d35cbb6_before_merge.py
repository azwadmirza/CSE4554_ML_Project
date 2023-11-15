    def copy(self, reference, user_channel, force=False, packages=None):
        """
        param packages: None=No binaries, True=All binaries, else list of IDs
        """
        from conans.client.cmd.copy import cmd_copy
        remotes = self._cache.registry.load_remotes()
        # FIXME: conan copy does not support short-paths in Windows
        ref = ConanFileReference.loads(reference)
        cmd_copy(ref, user_channel, packages, self._cache,
                 self._user_io, self._remote_manager, self._loader, remotes, force=force)