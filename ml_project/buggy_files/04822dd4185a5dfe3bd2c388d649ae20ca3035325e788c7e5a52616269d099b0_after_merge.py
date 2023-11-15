    def _handle_node_cache(self, node, keep_build, processed_package_references, remotes):
        pref = node.pref
        assert pref.id, "Package-ID without value"
        assert pref.id != PACKAGE_ID_UNKNOWN, "Package-ID error: %s" % str(pref)
        conanfile = node.conanfile
        output = conanfile.output

        layout = self._cache.package_layout(pref.ref, conanfile.short_paths)

        with layout.package_lock(pref):
            if pref not in processed_package_references:
                processed_package_references.add(pref)
                if node.binary == BINARY_BUILD:
                    assert node.prev is None, "PREV for %s to be built should be None" % str(pref)
                    layout.package_remove(pref)
                    with layout.set_dirty_context_manager(pref):
                        pref = self._build_package(node, output, keep_build, remotes)
                    assert node.prev, "Node PREV shouldn't be empty"
                    assert node.pref.revision, "Node PREF revision shouldn't be empty"
                    assert pref.revision is not None, "PREV for %s to be built is None" % str(pref)
                elif node.binary in (BINARY_UPDATE, BINARY_DOWNLOAD):
                    # this can happen after a re-evaluation of packageID with Package_ID_unknown
                    self._download_pkg(layout, node)
                elif node.binary == BINARY_CACHE:
                    assert node.prev, "PREV for %s is None" % str(pref)
                    output.success('Already installed!')
                    log_package_got_from_local_cache(pref)
                    self._recorder.package_fetched_from_cache(pref)

            package_folder = layout.package(pref)
            assert os.path.isdir(package_folder), ("Package '%s' folder must exist: %s\n"
                                                   % (str(pref), package_folder))
            # Call the info method
            self._call_package_info(conanfile, package_folder, ref=pref.ref)
            self._recorder.package_cpp_info(pref, conanfile.cpp_info)