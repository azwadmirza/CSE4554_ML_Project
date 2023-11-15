    def _propagate_info(node, using_build_profile):
        # Get deps_cpp_info from upstream nodes
        node_order = [n for n in node.public_closure if n.binary != BINARY_SKIP]
        # List sort is stable, will keep the original order of the closure, but prioritize levels
        conan_file = node.conanfile
        conan_file._conan_using_build_profile = using_build_profile  # FIXME: Not the best place to assign it
        transitive = [it for it in node.transitive_closure.values()]

        br_host = []
        for it in node.dependencies:
            if it.require.build_require_context == CONTEXT_HOST:
                br_host.extend(it.dst.transitive_closure.values())

        for n in node_order:
            if n not in transitive:
                conan_file.output.info("Applying build-requirement: %s" % str(n.ref))

            if not using_build_profile:  # Do not touch anything
                conan_file.deps_user_info[n.ref.name] = n.conanfile.user_info
                conan_file.deps_cpp_info.update(n.conanfile._conan_dep_cpp_info, n.ref.name)
                conan_file.deps_env_info.update(n.conanfile.env_info, n.ref.name)
            else:
                if n in transitive or n in br_host:
                    conan_file.deps_cpp_info.update(n.conanfile._conan_dep_cpp_info, n.ref.name)
                else:
                    env_info = EnvInfo()
                    env_info._values_ = n.conanfile.env_info._values_.copy()
                    # Add cpp_info.bin_paths/lib_paths to env_info (it is needed for runtime)
                    env_info.DYLD_LIBRARY_PATH.extend(n.conanfile._conan_dep_cpp_info.lib_paths)
                    env_info.DYLD_LIBRARY_PATH.extend(n.conanfile._conan_dep_cpp_info.framework_paths)
                    env_info.LD_LIBRARY_PATH.extend(n.conanfile._conan_dep_cpp_info.lib_paths)
                    env_info.PATH.extend(n.conanfile._conan_dep_cpp_info.bin_paths)
                    conan_file.deps_env_info.update(env_info, n.ref.name)

        # Update the info but filtering the package values that not apply to the subtree
        # of this current node and its dependencies.
        subtree_libnames = [node.ref.name for node in node_order]
        add_env_conaninfo(conan_file, subtree_libnames)