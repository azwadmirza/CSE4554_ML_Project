    def find_spec(self, name, path, target=None):
        # If jvm is not started then we just check against the TLDs
        if not _jpype.isStarted():
            base = name.partition('.')[0]
            if not base in _JDOMAINS:
                return None
            raise ImportError("Attempt to create Java package '%s' without jvm" % name)

        # Check for aliases
        if name in _JDOMAINS:
            jname = _JDOMAINS[name]
            if not _jpype.isPackage(jname):
                raise ImportError("Java package '%s' not found, requested by alias '%s'" % (jname, name))
            ms = _ModuleSpec(name, self)
            ms._jname = jname
            return ms

        # Check if it is a TLD
        parts = name.rpartition('.')

        # Use the parent module to simplify name mangling
        if not parts[1] and _jpype.isPackage(parts[2]):
            ms = _ModuleSpec(name, self)
            ms._jname = name
            return ms

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
                _jpype.JClass("java.lang.Class").forName(name)
                raise ImportError("Class `%s` was found but was not expected" % name)
            # Not found is acceptable
            except Exception as ex:
                raise ImportError("Failed to import '%s'" % name) from ex

        # Import the java module
        return _ModuleSpec(name, self)