    def __call__(self, require):
        try:
            python_require = self._cached_requires[require]
        except KeyError:
            r = ConanFileReference.loads(require)
            requirement = Requirement(r)
            self._range_resolver.resolve(requirement, "python_require", update=False,
                                         remote_name=None)
            r = requirement.conan_reference
            result = self._proxy.get_recipe(r, False, False, remote_name=None,
                                            recorder=ActionRecorder())
            path, _, _, reference = result
            module, _ = parse_conanfile(path)
            python_require = PythonRequire(reference, module)
            self._cached_requires[require] = python_require
        self._requires.append(python_require)
        return python_require.module