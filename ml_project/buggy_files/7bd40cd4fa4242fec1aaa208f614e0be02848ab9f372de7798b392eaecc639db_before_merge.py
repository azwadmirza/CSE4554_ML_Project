    def do_install(self,
                   keep_prefix=False,
                   keep_stage=False,
                   install_deps=True,
                   install_self=True,
                   skip_patch=False,
                   verbose=False,
                   make_jobs=None,
                   run_tests=False,
                   fake=False,
                   explicit=False,
                   dirty=False,
                   install_phases=install_phases):
        """Called by commands to install a package and its dependencies.

        Package implementations should override install() to describe
        their build process.

        :param keep_prefix: Keep install prefix on failure. By default, \
            destroys it.
        :param keep_stage: By default, stage is destroyed only if there are \
            no exceptions during build. Set to True to keep the stage
            even with exceptions.
        :param install_deps: Install dependencies before installing this \
            package
        :param install_self: Install this package once dependencies have \
            been installed.
        :param fake: Don't really build; install fake stub files instead.
        :param skip_patch: Skip patch stage of build if True.
        :param verbose: Display verbose build output (by default, suppresses \
            it)
        :param dirty: Don't clean the build environment before installing.
        :param make_jobs: Number of make jobs to use for install. Default is \
            ncpus
        :param force: Install again, even if already installed.
        :param run_tests: Run tests within the package's install()
        """
        if not self.spec.concrete:
            raise ValueError("Can only install concrete packages: %s."
                             % self.spec.name)

        # No installation needed if package is external
        if self.spec.external:
            tty.msg("%s is externally installed in %s" %
                    (self.name, self.spec.external))
            return

        # Ensure package is not already installed
        layout = spack.install_layout
        if 'install' in install_phases and layout.check_installed(self.spec):
            tty.msg("%s is already installed in %s" % (self.name, self.prefix))
            rec = spack.installed_db.get_record(self.spec)
            if (not rec.explicit) and explicit:
                with spack.installed_db.write_transaction():
                    rec = spack.installed_db.get_record(self.spec)
                    rec.explicit = True
            return

        tty.msg("Installing %s" % self.name)

        # First, install dependencies recursively.
        if install_deps:
            for dep in self.spec.dependencies():
                dep.package.do_install(
                    keep_prefix=keep_prefix,
                    keep_stage=keep_stage,
                    install_deps=install_deps,
                    install_self=True,
                    fake=fake,
                    skip_patch=skip_patch,
                    verbose=verbose,
                    make_jobs=make_jobs,
                    run_tests=run_tests,
                    dirty=dirty)

        # The rest of this function is to install ourself,
        # once deps have been installed.
        if not install_self:
            return

        # Set run_tests flag before starting build.
        self.run_tests = run_tests

        # Set parallelism before starting build.
        self.make_jobs = make_jobs

        # ------------------- BEGIN def build_process()
        # Then install the package itself.
        def build_process():
            """Forked for each build. Has its own process and python
               module space set up by build_environment.fork()."""

            start_time = time.time()
            if not fake:
                if not skip_patch:
                    self.do_patch()
                else:
                    self.do_stage()

            tty.msg("Building %s" % self.name)

            self.stage.keep = keep_stage
            self.install_phases = install_phases
            self.build_directory = join_path(self.stage.path, 'spack-build')
            self.source_directory = self.stage.source_path

            with self.stage:
                # Run the pre-install hook in the child process after
                # the directory is created.
                spack.hooks.pre_install(self)

                if fake:
                    self.do_fake_install()
                else:
                    # Do the real install in the source directory.
                    self.stage.chdir_to_source()

                    # Save the build environment in a file before building.
                    env_path = join_path(os.getcwd(), 'spack-build.env')

                    try:
                        # Redirect I/O to a build log (and optionally to
                        # the terminal)
                        log_path = join_path(os.getcwd(), 'spack-build.out')
                        log_file = open(log_path, 'w')
                        with log_output(log_file, verbose, sys.stdout.isatty(),
                                        True):
                            dump_environment(env_path)
                            self.install(self.spec, self.prefix)

                    except ProcessError as e:
                        # Annotate ProcessErrors with the location of
                        # the build log
                        e.build_log = log_path
                        raise e

                    # Ensure that something was actually installed.
                    if 'install' in self.install_phases:
                        self.sanity_check_prefix()

                    # Copy provenance into the install directory on success
                    if 'provenance' in self.install_phases:
                        log_install_path = layout.build_log_path(self.spec)
                        env_install_path = layout.build_env_path(self.spec)
                        packages_dir = layout.build_packages_path(self.spec)

                        # Remove first if we're overwriting another build
                        # (can happen with spack setup)
                        try:
                            # log_install_path and env_install_path are here
                            shutil.rmtree(packages_dir)
                        except:
                            pass

                        install(log_path, log_install_path)
                        install(env_path, env_install_path)
                        dump_packages(self.spec, packages_dir)

                # Run post install hooks before build stage is removed.
                spack.hooks.post_install(self)

            # Stop timer.
            self._total_time = time.time() - start_time
            build_time = self._total_time - self._fetch_time

            tty.msg("Successfully installed %s" % self.name,
                    "Fetch: %s.  Build: %s.  Total: %s." %
                    (_hms(self._fetch_time), _hms(build_time),
                     _hms(self._total_time)))
            print_pkg(self.prefix)
        # ------------------- END def build_process()

        try:
            # Create the install prefix and fork the build process.
            spack.install_layout.create_install_directory(self.spec)
        except directory_layout.InstallDirectoryAlreadyExistsError:
            if 'install' in install_phases:
                # Abort install if install directory exists.
                # But do NOT remove it (you'd be overwriting someone's data)
                tty.warn("Keeping existing install prefix in place.")
                raise
            else:
                # We're not installing anyway, so don't worry if someone
                # else has already written in the install directory
                pass

        try:
            spack.build_environment.fork(self, build_process, dirty=dirty)
        except:
            # remove the install prefix if anything went wrong during install.
            if not keep_prefix:
                self.remove_prefix()
            else:
                tty.warn("Keeping install prefix in place despite error.",
                         "Spack will think this package is installed. " +
                         "Manually remove this directory to fix:",
                         self.prefix,
                         wrap=False)
            raise

        # note: PARENT of the build process adds the new package to
        # the database, so that we don't need to re-read from file.
        spack.installed_db.add(
            self.spec, spack.install_layout, explicit=explicit)