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

            with contextlib.nested(self.stage, self._prefix_write_lock()):
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