    def inspect(self, path, attributes, remote_name=None):
        remotes = self.app.load_remotes(remote_name=remote_name)
        try:
            ref = ConanFileReference.loads(path)
        except ConanException:
            conanfile_path = _get_conanfile_path(path, get_cwd(), py=True)
            conanfile = self.app.loader.load_named(conanfile_path, None, None, None, None)
        else:
            update = True if remote_name else False
            result = self.app.proxy.get_recipe(ref, update, update, remotes, ActionRecorder())
            conanfile_path, _, _, ref = result
            conanfile = self.app.loader.load_basic(conanfile_path)
            conanfile.name = ref.name
            conanfile.version = str(ref.version) \
                if os.environ.get(CONAN_V2_MODE_ENVVAR, False) else ref.version

        result = OrderedDict()
        if not attributes:
            attributes = ['name', 'version', 'url', 'homepage', 'license', 'author',
                          'description', 'topics', 'generators', 'exports', 'exports_sources',
                          'short_paths', 'apply_env', 'build_policy', 'revision_mode', 'settings',
                          'options', 'default_options']
        for attribute in attributes:
            try:
                attr = getattr(conanfile, attribute)
                result[attribute] = attr
            except AttributeError:
                result[attribute] = ''
        return result