    def _use(self, backend_name=None):
        """Select a backend by name. See class docstring for details.
        """
        # See if we're in a specific testing mode, if so DONT check to see
        # if it's a valid backend. If it isn't, it's a good thing we
        # get an error later because we should have decorated our test
        # with requires_application()
        test_name = os.getenv('_VISPY_TESTING_APP', None)

        # Check whether the given name is valid
        if backend_name is not None:
            if backend_name.lower() == 'default':
                backend_name = None  # Explicitly use default, avoid using test
            elif backend_name.lower() not in BACKENDMAP:
                raise ValueError('backend_name must be one of %s or None, not '
                                 '%r' % (BACKEND_NAMES, backend_name))
        elif test_name is not None:
            backend_name = test_name.lower()
            assert backend_name in BACKENDMAP

        # Should we try and load any backend, or just this specific one?
        try_others = backend_name is None

        # Get backends to try ...
        imported_toolkits = []  # Backends for which the native lib is imported
        backends_to_try = []
        if not try_others:
            # We should never hit this, since we check above
            assert backend_name.lower() in BACKENDMAP.keys()
            # Add it
            backends_to_try.append(backend_name.lower())
        else:
            # See if a backend is loaded
            for name, module_name, native_module_name in CORE_BACKENDS:
                if native_module_name and native_module_name in sys.modules:
                    imported_toolkits.append(name.lower())
                    backends_to_try.append(name.lower())
            # See if a default is given
            default_backend = config['default_backend'].lower()
            if default_backend.lower() in BACKENDMAP.keys():
                if default_backend not in backends_to_try:
                    backends_to_try.append(default_backend)
            # After this, try each one
            for name, module_name, native_module_name in CORE_BACKENDS:
                name = name.lower()
                if name not in backends_to_try:
                    backends_to_try.append(name)

        # Now try each one
        for key in backends_to_try:
            name, module_name, native_module_name = BACKENDMAP[key]
            TRIED_BACKENDS.append(name)
            mod_name = 'backends.' + module_name
            __import__(mod_name, globals(), level=1)
            mod = getattr(backends, module_name)
            if not mod.available:
                msg = ('Could not import backend "%s":\n%s'
                       % (name, str(mod.why_not)))
                if not try_others:
                    # Fail if user wanted to use a specific backend
                    raise RuntimeError(msg)
                elif key in imported_toolkits:
                    # Warn if were unable to use an already imported toolkit
                    msg = ('Although %s is already imported, the %s backend '
                           'could not\nbe used ("%s"). \nNote that running '
                           'multiple GUI toolkits simultaneously can cause '
                           'side effects.' % 
                           (native_module_name, name, str(mod.why_not))) 
                    logger.warning(msg)
                else:
                    # Inform otherwise
                    logger.info(msg)
            else:
                # Success!
                self._backend_module = mod
                logger.debug('Selected backend %s' % module_name)
                break
        else:
            raise RuntimeError('Could not import any of the backends.')

        # Store classes for app backend and canvas backend
        self._backend = self.backend_module.ApplicationBackend()