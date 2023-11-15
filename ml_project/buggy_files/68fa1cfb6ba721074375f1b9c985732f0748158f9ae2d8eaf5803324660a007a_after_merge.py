    def create(self, profile_name=None, settings=None,
               options=None, env=None, scope=None, test_folder=None, not_export=False, build=None,
               keep_source=False, verify=None,
               manifests=None, manifests_interactive=None,
               remote=None, update=False, cwd=None,
               user=None, channel=None, name=None, version=None):

        settings = settings or []
        options = options or []
        env = env or []
        cwd = prepare_cwd(cwd)

        if not name or not version:
            conanfile_path = os.path.join(cwd, "conanfile.py")
            conanfile = load_conanfile_class(conanfile_path)
            name, version = conanfile.name, conanfile.version
            if not name or not version:
                raise ConanException("conanfile.py doesn't declare package name or version")

        reference = ConanFileReference(name, version, user, channel)
        scoped_output = ScopedOutput(str(reference), self._user_io.out)
        # Forcing an export!
        if not not_export:
            scoped_output.highlight("Exporting package recipe")
            self._manager.export(user, channel, cwd, keep_source=keep_source, name=name,
                                 version=version)

        if build is None:  # Not specified, force build the tested library
            build = [name]

        manifests = _parse_manifests_arguments(verify, manifests, manifests_interactive, cwd)
        manifest_folder, manifest_interactive, manifest_verify = manifests
        profile = profile_from_args(profile_name, settings, options, env, scope,
                                    cwd, self._client_cache.profiles_path)
        self._manager.install(reference=reference,
                              current_path=cwd,
                              manifest_folder=manifest_folder,
                              manifest_verify=manifest_verify,
                              manifest_interactive=manifest_interactive,
                              remote=remote,
                              profile=profile,
                              build_modes=build,
                              update=update
                              )

        test_folders = [test_folder] if test_folder else ["test_package", "test"]
        for test_folder_name in test_folders:
            test_folder = os.path.join(cwd, test_folder_name)
            test_conanfile_path = os.path.join(test_folder, "conanfile.py")
            if os.path.exists(test_conanfile_path):
                break
        else:
            self._user_io.out.warn("test package folder not available, or it doesn't have "
                                   "a conanfile.py\nIt is recommended to set a 'test_package' "
                                   "while creating packages")
            return

        scoped_output.highlight("Testing with 'test_package'")
        sha = hashlib.sha1("".join(options + settings).encode()).hexdigest()
        build_folder = os.path.join(test_folder, "build", sha)
        rmdir(build_folder)

        test_conanfile = os.path.join(test_folder, CONANFILE)
        self._manager.install(inject_require=reference,
                              reference=test_folder,
                              current_path=build_folder,
                              manifest_folder=manifest_folder,
                              manifest_verify=manifest_verify,
                              manifest_interactive=manifest_interactive,
                              remote=remote,
                              profile=profile,
                              update=update,
                              generators=["txt"]
                              )
        self._manager.build(test_conanfile, test_folder, build_folder, package_folder=None,
                            test=str(reference))