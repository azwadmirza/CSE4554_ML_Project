    def add(self, reference, private=False, override=False, dev=False):
        """ to define requirements by the user in text, prior to any propagation
        """
        assert isinstance(reference, six.string_types)
        if dev and not self.allow_dev:
            return

        conan_reference = ConanFileReference.loads(reference)
        name = conan_reference.name

        new_requirement = Requirement(conan_reference, private, override, dev)
        old_requirement = self.get(name)
        if old_requirement and old_requirement != new_requirement:
            self.output.werror("Duplicated requirement %s != %s"
                               % (old_requirement, new_requirement))
        else:
            self[name] = new_requirement