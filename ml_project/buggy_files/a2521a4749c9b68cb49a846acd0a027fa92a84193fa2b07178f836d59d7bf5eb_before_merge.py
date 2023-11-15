    def generate_target_install(self, d):
        for t in self.build.get_targets().values():
            if not t.should_install():
                continue
            outdirs, custom_install_dir = self.get_target_install_dirs(t)
            # Sanity-check the outputs and install_dirs
            num_outdirs, num_out = len(outdirs), len(t.get_outputs())
            if num_outdirs != 1 and num_outdirs != num_out:
                m = 'Target {!r} has {} outputs: {!r}, but only {} "install_dir"s were found.\n' \
                    "Pass 'false' for outputs that should not be installed and 'true' for\n" \
                    'using the default installation directory for an output.'
                raise MesonException(m.format(t.name, num_out, t.get_outputs(), num_outdirs))
            install_mode = t.get_custom_install_mode()
            # Install the target output(s)
            if isinstance(t, build.BuildTarget):
                should_strip = self.get_option_for_target('strip', t)
                # Install primary build output (library/executable/jar, etc)
                # Done separately because of strip/aliases/rpath
                if outdirs[0] is not False:
                    mappings = self.get_target_link_deps_mappings(t, d.prefix)
                    i = TargetInstallData(self.get_target_filename(t), outdirs[0],
                                          t.get_aliases(), should_strip, mappings,
                                          t.install_rpath, install_mode)
                    d.targets.append(i)
                    # On toolchains/platforms that use an import library for
                    # linking (separate from the shared library with all the
                    # code), we need to install that too (dll.a/.lib).
                    if isinstance(t, (build.SharedLibrary, build.SharedModule, build.Executable)) and t.get_import_filename():
                        if custom_install_dir:
                            # If the DLL is installed into a custom directory,
                            # install the import library into the same place so
                            # it doesn't go into a surprising place
                            implib_install_dir = outdirs[0]
                        else:
                            implib_install_dir = self.environment.get_import_lib_dir()
                        # Install the import library.
                        i = TargetInstallData(self.get_target_filename_for_linking(t),
                                              implib_install_dir, {}, False, {}, '', install_mode)
                        d.targets.append(i)
                # Install secondary outputs. Only used for Vala right now.
                if num_outdirs > 1:
                    for output, outdir in zip(t.get_outputs()[1:], outdirs[1:]):
                        # User requested that we not install this output
                        if outdir is False:
                            continue
                        f = os.path.join(self.get_target_dir(t), output)
                        i = TargetInstallData(f, outdir, {}, False, {}, None, install_mode)
                        d.targets.append(i)
            elif isinstance(t, build.CustomTarget):
                # If only one install_dir is specified, assume that all
                # outputs will be installed into it. This is for
                # backwards-compatibility and because it makes sense to
                # avoid repetition since this is a common use-case.
                #
                # To selectively install only some outputs, pass `false` as
                # the install_dir for the corresponding output by index
                if num_outdirs == 1 and num_out > 1:
                    for output in t.get_outputs():
                        f = os.path.join(self.get_target_dir(t), output)
                        i = TargetInstallData(f, outdirs[0], {}, False, {}, None, install_mode)
                        d.targets.append(i)
                else:
                    for output, outdir in zip(t.get_outputs(), outdirs):
                        # User requested that we not install this output
                        if outdir is False:
                            continue
                        f = os.path.join(self.get_target_dir(t), output)
                        i = TargetInstallData(f, outdir, {}, False, {}, None, install_mode)
                        d.targets.append(i)