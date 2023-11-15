    def _compute_package_id(self, node, default_package_id_mode, default_python_requires_id_mode):
        """
        Compute the binary package ID of this node
        :param node: the node to compute the package-ID
        :param default_package_id_mode: configuration of the package-ID mode
        """
        # TODO Conan 2.0. To separate the propagation of the graph (options) of the package-ID
        # A bit risky to be done now
        conanfile = node.conanfile
        neighbors = node.neighbors()
        if not self._fixed_package_id:
            direct_reqs = []  # of PackageReference
            indirect_reqs = set()  # of PackageReference, avoid duplicates
            for neighbor in neighbors:
                ref, nconan = neighbor.ref, neighbor.conanfile
                direct_reqs.append(neighbor.pref)
                indirect_reqs.update(nconan.info.requires.refs())
            # Make sure not duplicated
            indirect_reqs.difference_update(direct_reqs)
        else:
            node.id_direct_prefs = set()  # of PackageReference
            node.id_indirect_prefs = set()  # of PackageReference, avoid duplicates
            for neighbor in neighbors:
                node.id_direct_prefs.add(neighbor.pref)
                node.id_indirect_prefs.update(neighbor.id_direct_prefs)
                node.id_indirect_prefs.update(neighbor.id_indirect_prefs)
            # Make sure not duplicated, totally necessary
            node.id_indirect_prefs.difference_update(node.id_direct_prefs)
            direct_reqs = node.id_direct_prefs
            indirect_reqs = node.id_indirect_prefs

        python_requires = getattr(conanfile, "python_requires", None)
        if python_requires:
            if isinstance(python_requires, dict):
                python_requires = None  # Legacy python-requires do not change package-ID
            else:
                python_requires = python_requires.all_refs()
        conanfile.info = ConanInfo.create(conanfile.settings.values,
                                          conanfile.options.values,
                                          direct_reqs,
                                          indirect_reqs,
                                          default_package_id_mode=default_package_id_mode,
                                          python_requires=python_requires,
                                          default_python_requires_id_mode=
                                          default_python_requires_id_mode)

        # Once we are done, call package_id() to narrow and change possible values
        with conanfile_exception_formatter(str(conanfile), "package_id"):
            with conan_v2_property(conanfile, 'cpp_info',
                                   "'self.cpp_info' access in package_id() method is deprecated"):
                conanfile.package_id()

        info = conanfile.info
        node.package_id = info.package_id()