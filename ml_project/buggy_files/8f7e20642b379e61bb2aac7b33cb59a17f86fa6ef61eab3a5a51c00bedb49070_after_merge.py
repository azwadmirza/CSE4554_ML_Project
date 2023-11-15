    def find_spec(self, name, path, target=None):
        # If jvm is not started then we just check against the TLDs
        if not _jpype.isStarted():
            base = name.partition('.')[0]
            if not base in _JDOMAINS:
                return None
            raise ImportError("Attempt to create java modules without jvm")

        # Check if it is a TLD
        parts = name.rpartition('.')
        if not parts[1] and _jpype.isPackage(parts[2]):
            return _ModuleSpec(name, self)

        if not parts[1] and not _jpype.isPackage(parts[0]):
            return None

        base = sys.modules.get(parts[0], None)
        if not base or not isinstance(base, _jpype._JPackage):
            return None

        # Support for external modules in java tree
        name = unwrap(name)
        for customizer in _CUSTOMIZERS:
            if customizer.canCustomize(name):
                return customizer.getSpec(name)

        # Using isPackage eliminates need for registering tlds
        if not hasattr(base, parts[2]):
            # If the base is a Java package and it wasn't found in the
            # package using getAttr, then we need to emit an error
            # so we produce a meaningful diagnositic.
            try:
                # Use forname because it give better diagnostics
                cls = _jpype.JClass("java.lang.Class").forName(name)
                return _jpype.JClass(cls)
            # Not found is acceptable
            except Exception as ex:
                raise ImportError("Failed to import '%s'" % name) from ex

        # Import the java module
        return _ModuleSpec(name, self)