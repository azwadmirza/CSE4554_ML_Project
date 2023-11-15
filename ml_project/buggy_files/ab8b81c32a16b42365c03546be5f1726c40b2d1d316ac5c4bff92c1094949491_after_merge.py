    def _compute_private_nodes(self, deps_graph, build_mode):
        """ computes a list of nodes that are not required to be built, as they are
        private requirements of already available shared libraries as binaries
        """
        private_closure = deps_graph.private_nodes()
        skippable_nodes = []
        for private_node, private_requirers in private_closure:
            for private_requirer in private_requirers:
                conan_ref, conan_file = private_requirer
                if conan_ref is None:
                    continue
                package_id = conan_file.info.package_id()
                package_reference = PackageReference(conan_ref, package_id)
                package_folder = self._paths.package(package_reference)
                if not path_exists(package_folder, self._paths.store):
                    if not self._force_build(conan_ref, build_mode):  # Not download package
                        self._user_io.out.info('Package for %s does not exist' % str(conan_ref))
                        if not self._retrieve_remote_package(package_reference):
                            break
            else:
                skippable_nodes.append(private_node)
        return skippable_nodes