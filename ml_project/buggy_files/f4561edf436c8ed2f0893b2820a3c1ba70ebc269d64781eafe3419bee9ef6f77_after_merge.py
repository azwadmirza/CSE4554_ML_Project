    def _retrieve_remote_package(self, package_reference, output, remote=None):

        if remote is None:
            remote = self._registry.get_ref(package_reference.conan)
        if not remote:
            output.warn("Package doesn't have a remote defined. "
                        "Probably created locally and not uploaded")
            return False
        package_id = str(package_reference.package_id)
        try:
            output.info("Looking for package %s in remote '%s' " % (package_id, remote.name))
            # Will raise if not found NotFoundException
            package_path = self._client_cache.package(package_reference)
            self._remote_manager.get_package(package_reference, package_path, remote)
            output.success('Package installed %s' % package_id)
            return True
        except ConanConnectionError:
            raise  # This shouldn't be skipped
        except ConanException as e:
            output.warn('Binary for %s not in remote: %s' % (package_id, str(e)))
            return False