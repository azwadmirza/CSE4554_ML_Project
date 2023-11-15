    def to_requirement(self, dist):
        req = dist.as_requirement()

        # pkg_resources.Distribution.as_requirement returns requirements in one of two forms:
        # 1.) project_name==version
        # 2.) project_name===version
        # The latter form is used whenever the distribution's version is non-standard. In those
        # cases we cannot append environment markers since `===` indicates a raw version string to
        # the right that should not be parsed and instead should be compared literally in full.
        # See:
        # + https://www.python.org/dev/peps/pep-0440/#arbitrary-equality
        # + https://github.com/pantsbuild/pex/issues/940
        operator, _ = req.specs[0]
        if operator == "===":
            return req

        markers = OrderedSet()

        # Here we map any wheel python requirement to the equivalent environment marker:
        # See:
        # + https://www.python.org/dev/peps/pep-0345/#requires-python
        # + https://www.python.org/dev/peps/pep-0508/#environment-markers
        python_requires = dist_metadata.requires_python(dist)
        if python_requires:
            markers.update(
                Marker(python_version)
                for python_version in sorted(
                    "python_version {operator} {version!r}".format(
                        operator=specifier.operator, version=specifier.version
                    )
                    for specifier in python_requires
                )
            )

        markers.update(self._markers_by_requirement_key.get(req.key, ()))

        if not markers:
            return req

        if len(markers) == 1:
            marker = next(iter(markers))
            req.marker = marker
            return req

        # We may have resolved with multiple paths to the dependency represented by dist and at least
        # two of those paths had (different) conditional requirements for dist based on environment
        # marker predicates. In that case, since the pip resolve succeeded, the implication is that the
        # environment markers are compatible; i.e.: their intersection selects the target interpreter.
        # Here we make that intersection explicit.
        # See: https://www.python.org/dev/peps/pep-0508/#grammar
        marker = " and ".join("({})".format(marker) for marker in markers)
        return Requirement.parse("{}; {}".format(req, marker))