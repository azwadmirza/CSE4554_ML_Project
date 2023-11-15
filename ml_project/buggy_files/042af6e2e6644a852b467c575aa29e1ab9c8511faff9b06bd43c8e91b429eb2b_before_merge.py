        def _retrieve_from_remote(remote):
            output.info("Trying with '%s'..." % remote.name)
            result = self._remote_manager.get_conanfile(conan_reference, remote)
            self._registry.set_ref(conan_reference, remote)
            return result