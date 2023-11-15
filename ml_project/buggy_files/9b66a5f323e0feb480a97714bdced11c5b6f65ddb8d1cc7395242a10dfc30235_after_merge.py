    def do_install(self,
                   keep_prefix=False,
                   keep_stage=False,
                   install_deps=True,
                   skip_patch=False,
                   verbose=False,
                   make_jobs=None,
                   run_tests=False,
                   fake=False,
                   explicit=False,
                   dirty=None,
                   **kwargs):
        """Called by commands to install a package and its dependencies.

        Package implementations should override install() to describe
        their build process.

        Args:
            keep_prefix (bool): Keep install prefix on failure. By default,
                destroys it.
            keep_stage (bool): By default, stage is destroyed only if there
                are no exceptions during build. Set to True to keep the stage
                even with exceptions.
            install_deps (bool): Install dependencies before installing this
                package
            skip_patch (bool): Skip patch stage of build if True.
            verbose (bool): Display verbose build output (by default,
                suppresses it)
            make_jobs (int): Number of make jobs to use for install. Default
                is ncpus
            run_tests (bool): Run tests within the package's install()
            fake (bool): Don't really build; install fake stub files instead.
            explicit (bool): True if package was explicitly installed, False
                if package was implicitly installed (as a dependency).
            dirty (bool): Don't clean the build environment before installing.
            force (bool): Install again, even if already installed.
        """
        if not self.spec.concrete:
            raise ValueError("Can only install concrete packages: %s."
                             % self.spec.name)

        # For external packages the workflow is simplified, and basically
        # consists in module file generation and registration in the DB
        if self.spec.external:
            return self._process_external_package(explicit)

        restage = kwargs.get('restage', False)
        partial = self.check_for_unfinished_installation(keep_prefix, restage)

        # Ensure package is not already installed
        layout = spack.store.layout
        with spack.store.db.prefix_read_lock(self.spec):
            if partial:
                tty.msg(
                    "Continuing from partial install of %s" % self.name)
            elif layout.check_installed(self.spec):
                msg = '{0.name} is already installed in {0.prefix}'
                tty.msg(msg.format(self))
                rec = spack.store.db.get_record(self.spec)
                return self._update_explicit_entry_in_db(rec, explicit)

        # Dirty argument takes precedence over dirty config setting.
        if dirty is None:
            dirty = spack.dirty

        self._do_install_pop_kwargs(kwargs)

        # First, install dependencies recursively.
        if install_deps:
            tty.debug('Installing {0} dependencies'.format(self.name))
            for dep in self.spec.dependencies():
                dep.package.do_install(
                    keep_prefix=keep_prefix,
                    keep_stage=keep_stage,
                    install_deps=install_deps,
                    fake=fake,
                    skip_patch=skip_patch,
                    verbose=verbose,
                    make_jobs=make_jobs,
                    run_tests=run_tests,
                    dirty=dirty,
                    **kwargs
                )

        tty.msg('Installing %s' % self.name)

        # Set run_tests flag before starting build.
        self.run_tests = run_tests

        # Set parallelism before starting build.
        self.make_jobs = make_jobs

        # Then install the package itself.
        def build_process(input_stream):
            """Forked for each build. Has its own process and python
               module space set up by build_environment.fork()."""

            # We are in the child process. This means that our sys.stdin is
            # equal to open(os.devnull). Python did this to prevent our process
            # and the parent process from possible simultaneous reading from
            # the original standard input. But we assume that the parent
            # process is not going to read from it till we are done here,
            # otherwise it should not have passed us the copy of the stream.
            # Thus, we are free to work with the the copy (input_stream)
            # however we want. For example, we might want to call functions
            # (e.g. input()) that implicitly read from whatever stream is
            # assigned to sys.stdin. Since we want them to work with the
            # original input stream, we are making the following assignment:
            sys.stdin = input_stream

            start_time = time.time()
            if not fake:
                if not skip_patch:
                    self.do_patch()
                else:
                    self.do_stage()

            tty.msg(
                'Building {0} [{1}]'.format(self.name, self.build_system_class)
            )

            self.stage.keep = keep_stage
            with self._stage_and_write_lock():
                # Run the pre-install hook in the child process after
                # the directory is created.
                spack.hooks.pre_install(self.spec)
                if fake:
                    self.do_fake_install()
                else:
                    # Do the real install in the source directory.
                    self.stage.chdir_to_source()

                    # Save the build environment in a file before building.
                    env_path = join_path(os.getcwd(), 'spack-build.env')

                    # Redirect I/O to a build log (and optionally to
                    # the terminal)
                    log_path = join_path(os.getcwd(), 'spack-build.out')

                    # FIXME : refactor this assignment
                    self.log_path = log_path
                    self.env_path = env_path
                    dump_environment(env_path)

                    # Spawn a daemon that reads from a pipe and redirects
                    # everything to log_path
                    redirection_context = log_output(
                        log_path,
                        echo=verbose,
                        force_color=sys.stdout.isatty(),
                        debug=True,
                        input_stream=input_stream
                    )
                    with redirection_context as log_redirection:
                        for phase_name, phase in zip(
                                self.phases, self._InstallPhase_phases):
                            tty.msg(
                                'Executing phase : \'{0}\''.format(phase_name)
                            )
                            # Redirect stdout and stderr to daemon pipe
                            with log_redirection:
                                getattr(self, phase)(
                                    self.spec, self.prefix)
                    self.log()
                # Run post install hooks before build stage is removed.
                spack.hooks.post_install(self.spec)

            # Stop timer.
            self._total_time = time.time() - start_time
            build_time = self._total_time - self._fetch_time

            tty.msg("Successfully installed %s" % self.name,
                    "Fetch: %s.  Build: %s.  Total: %s." %
                    (_hms(self._fetch_time), _hms(build_time),
                     _hms(self._total_time)))
            print_pkg(self.prefix)

        try:
            # Create the install prefix and fork the build process.
            if not os.path.exists(self.prefix):
                spack.store.layout.create_install_directory(self.spec)
            # Fork a child to do the actual installation
            spack.build_environment.fork(self, build_process, dirty=dirty)
            # If we installed then we should keep the prefix
            keep_prefix = self.last_phase is None or keep_prefix
            # note: PARENT of the build process adds the new package to
            # the database, so that we don't need to re-read from file.
            spack.store.db.add(
                self.spec, spack.store.layout, explicit=explicit
            )
        except directory_layout.InstallDirectoryAlreadyExistsError:
            # Abort install if install directory exists.
            # But do NOT remove it (you'd be overwriting someone else's stuff)
            tty.warn("Keeping existing install prefix in place.")
            raise
        except StopIteration as e:
            # A StopIteration exception means that do_install
            # was asked to stop early from clients
            tty.msg(e.message)
            tty.msg(
                'Package stage directory : {0}'.format(self.stage.source_path)
            )
        finally:
            # Remove the install prefix if anything went wrong during install.
            if not keep_prefix:
                self.remove_prefix()