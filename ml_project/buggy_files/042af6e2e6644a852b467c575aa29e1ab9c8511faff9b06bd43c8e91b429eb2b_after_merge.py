        def _retrieve_from_remote(remote):
            output.info("Trying with '%s'..." % remote.name)
            export_path = self._client_cache.export(conan_reference)
            result = self._remote_manager.get_recipe(conan_reference, export_path, remote)
            self._registry.set_ref(conan_reference, remote)
            return result