    def _load_pyreq_conanfile(self, loader, lock_python_requires, ref):
        recipe = self._proxy.get_recipe(ref, self._check_updates, self._update,
                                        remotes=self._remotes, recorder=ActionRecorder())
        path, _, _, new_ref = recipe
        conanfile, module = loader.load_basic_module(path, lock_python_requires, user=new_ref.user,
                                                     channel=new_ref.channel)
        conanfile.name = new_ref.name
        conanfile.version = new_ref.version

        if getattr(conanfile, "alias", None):
            ref = ConanFileReference.loads(conanfile.alias)
            conanfile, module, new_ref, path = self._load_pyreq_conanfile(loader,
                                                                          lock_python_requires,
                                                                          ref)
        return conanfile, module, new_ref, os.path.dirname(path)