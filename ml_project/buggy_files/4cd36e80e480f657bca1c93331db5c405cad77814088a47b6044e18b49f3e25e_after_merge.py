        def _refresh():
            export_path = self._client_cache.export(conan_reference)
            rmdir(export_path)
            # It might need to remove shortpath
            rmdir(self._client_cache.source(conan_reference), True)
            current_remote, _ = self._get_remote(conan_reference)
            output.info("Retrieving from remote '%s'..." % current_remote.name)
            self._remote_manager.get_recipe(conan_reference, export_path, current_remote)
            if self._update:
                output.info("Updated!")
            else:
                output.info("Installed!")