    def install(self, reference="", package=None, settings=None, options=None, env=None, scope=None, all=False,
                remote=None, werror=False, verify=default_manifest_folder, manifests=default_manifest_folder,
                manifests_interactive=default_manifest_folder, build=None, profile_name=None,
                update=False, generator=None, no_imports=False, filename=None, cwd=None):

        self._user_io.out.werror_active = werror
        cwd = prepare_cwd(cwd)

        try:
            ref = ConanFileReference.loads(reference)
        except:
            ref = os.path.normpath(os.path.join(cwd, reference))

        if all or package:  # Install packages without settings (fixed ids or all)
            if all:
                package = []
            if not reference or not isinstance(ref, ConanFileReference):
                raise ConanException("Invalid package recipe reference. "
                                     "e.g., MyPackage/1.2@user/channel")
            self._manager.download(ref, package, remote=remote)
        else:  # Classic install, package chosen with settings and options
            manifests = _parse_manifests_arguments(verify, manifests, manifests_interactive, cwd)
            manifest_folder, manifest_interactive, manifest_verify = manifests

            profile = profile_from_args(profile_name, settings, options, env, scope, cwd,
                                        self._client_cache.profiles_path)

            self._manager.install(reference=ref,
                                  current_path=cwd,
                                  remote=remote,
                                  profile=profile,
                                  build_modes=build,
                                  filename=filename,
                                  update=update,
                                  manifest_folder=manifest_folder,
                                  manifest_verify=manifest_verify,
                                  manifest_interactive=manifest_interactive,
                                  generators=generator,
                                  no_imports=no_imports)