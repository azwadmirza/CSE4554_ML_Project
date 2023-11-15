    def concretize_architecture(self, spec):
        """If the spec is empty provide the defaults of the platform. If the
        architecture is not a string type, then check if either the platform,
        target or operating system are concretized. If any of the fields are
        changed then return True. If everything is concretized (i.e the
        architecture attribute is a namedtuple of classes) then return False.
        If the target is a string type, then convert the string into a
        concretized architecture. If it has no architecture and the root of the
        DAG has an architecture, then use the root otherwise use the defaults
        on the platform.
        """
        root_arch = spec.root.architecture
        sys_arch = spack.spec.ArchSpec(spack.architecture.sys_type())
        spec_changed = False

        if spec.architecture is None:
            spec.architecture = spack.spec.ArchSpec(sys_arch)
            spec_changed = True

        default_archs = list(x for x in [root_arch, sys_arch] if x)
        for arch in default_archs:
            if spec.architecture.concrete:
                break

            replacement_fields = [k for k, v in iteritems(arch.to_cmp_dict())
                                  if v and not getattr(spec.architecture, k)]
            for field in replacement_fields:
                setattr(spec.architecture, field, getattr(arch, field))
                spec_changed = True

        if not spec.architecture.concrete:
            raise InsufficientArchitectureInfoError(spec, default_archs)

        return spec_changed