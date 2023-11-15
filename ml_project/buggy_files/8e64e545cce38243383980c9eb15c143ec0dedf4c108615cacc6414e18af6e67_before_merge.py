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
            # (e.g. raw_input()) that implicitly read from whatever stream is
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
                spack.hooks.pre_install(self)
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
                spack.hooks.post_install(self)

            # Stop timer.
            self._total_time = time.time() - start_time
            build_time = self._total_time - self._fetch_time

            tty.msg("Successfully installed %s" % self.name,
                    "Fetch: %s.  Build: %s.  Total: %s." %
                    (_hms(self._fetch_time), _hms(build_time),
                     _hms(self._total_time)))
            print_pkg(self.prefix)