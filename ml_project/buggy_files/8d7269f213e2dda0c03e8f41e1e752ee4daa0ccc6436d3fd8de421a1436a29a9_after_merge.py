    def _evaluate_node(self, node, build_mode, update, evaluated_nodes, remote_name):
        assert node.binary is None, "Node.binary should be None"
        assert node.package_id is not None, "Node.package_id shouldn't be None"

        ref, conanfile = node.ref, node.conanfile
        pref = PackageReference(ref, node.package_id)

        # Check that this same reference hasn't already been checked
        previous_nodes = evaluated_nodes.get(pref)
        if previous_nodes:
            previous_nodes.append(node)
            previous_node = previous_nodes[0]
            node.binary = previous_node.binary
            node.binary_remote = previous_node.binary_remote
            node.prev = previous_node.prev
            return
        evaluated_nodes[pref] = [node]

        output = conanfile.output

        if node.recipe == RECIPE_EDITABLE:
            node.binary = BINARY_EDITABLE
            # TODO: PREV?
            return

        if build_mode.forced(conanfile, ref):
            output.warn('Forced build from source')
            node.binary = BINARY_BUILD
            node.prev = None
            return

        package_folder = self._cache.package(pref, short_paths=conanfile.short_paths)

        # Check if dirty, to remove it
        with self._cache.package_lock(pref):
            assert node.recipe != RECIPE_EDITABLE, "Editable package shouldn't reach this code"
            if is_dirty(package_folder):
                output.warn("Package is corrupted, removing folder: %s" % package_folder)
                rmdir(package_folder)  # Do not remove if it is EDITABLE

            if self._cache.config.revisions_enabled:
                metadata = self._cache.package_layout(pref.ref).load_metadata()
                rec_rev = metadata.packages[pref.id].recipe_revision
                if rec_rev and rec_rev != node.ref.revision:
                    output.warn("The package {} doesn't belong "
                                "to the installed recipe revision, removing folder".format(pref))
                    rmdir(package_folder)

        if remote_name:
            remote = self._registry.remotes.get(remote_name)
        else:
            # If the remote_name is not given, follow the binary remote, or
            # the recipe remote
            # If it is defined it won't iterate (might change in conan2.0)
            remote = self._registry.prefs.get(pref) or self._registry.refs.get(ref)
        remotes = self._registry.remotes.list

        if os.path.exists(package_folder):
            if update:
                if remote:
                    try:
                        tmp = self._remote_manager.get_package_manifest(pref, remote)
                        upstream_manifest, pref = tmp
                    except NotFoundException:
                        output.warn("Can't update, no package in remote")
                    except NoRemoteAvailable:
                        output.warn("Can't update, no remote defined")
                    else:
                        if self._check_update(upstream_manifest, package_folder, output, node):
                            node.binary = BINARY_UPDATE
                            node.prev = pref.revision  # With revision
                            if build_mode.outdated:
                                info, pref = self._remote_manager.get_package_info(pref, remote)
                                package_hash = info.recipe_hash
                elif remotes:
                    pass
                else:
                    output.warn("Can't update, no remote defined")
            if not node.binary:
                node.binary = BINARY_CACHE
                metadata = self._cache.package_layout(pref.ref).load_metadata()
                node.prev = metadata.packages[pref.id].revision
                assert node.prev, "PREV for %s is None: %s" % (str(pref), metadata.dumps())
                package_hash = ConanInfo.load_from_package(package_folder).recipe_hash

        else:  # Binary does NOT exist locally
            remote_info = None
            if remote:
                try:
                    remote_info, pref = self._remote_manager.get_package_info(pref, remote)
                except NotFoundException:
                    pass
                except Exception:
                    conanfile.output.error("Error downloading binary package: '{}'".format(pref))
                    raise

            # If the "remote" came from the registry but the user didn't specified the -r, with
            # revisions iterate all remotes
            if not remote or (not remote_info and self._cache.config.revisions_enabled
                              and not remote_name):
                for r in remotes:
                    try:
                        remote_info, pref = self._remote_manager.get_package_info(pref, r)
                    except NotFoundException:
                        pass
                    else:
                        if remote_info:
                            remote = r
                            break

            if remote_info:
                node.binary = BINARY_DOWNLOAD
                node.prev = pref.revision
                package_hash = remote_info.recipe_hash
            else:
                if build_mode.allowed(conanfile):
                    node.binary = BINARY_BUILD
                else:
                    node.binary = BINARY_MISSING
                node.prev = None

        if build_mode.outdated:
            if node.binary in (BINARY_CACHE, BINARY_DOWNLOAD, BINARY_UPDATE):
                local_recipe_hash = self._cache.package_layout(ref).recipe_manifest().summary_hash
                if local_recipe_hash != package_hash:
                    output.info("Outdated package!")
                    node.binary = BINARY_BUILD
                    node.prev = None
                else:
                    output.info("Package is up to date")

        node.binary_remote = remote