  def post_fork_child(self):
    """Post-fork child process callback executed via ProcessManager.daemonize()."""
    # Set the Exiter exception hook post-fork so as not to affect the pantsd processes exception
    # hook with socket-specific behavior. Note that this intentionally points the faulthandler
    # trace stream to sys.stderr, which at this point is still a _LoggerStream object writing to
    # the `pantsd.log`. This ensures that in the event of e.g. a hung but detached pantsd-runner
    # process that the stacktrace output lands deterministically in a known place vs to a stray
    # terminal window.
    # TODO: test the above!
    ExceptionSink.reset_exiter(self._exiter)

    ExceptionSink.reset_interactive_output_stream(sys.stderr.buffer if PY3 else sys.stderr)

    # Ensure anything referencing sys.argv inherits the Pailgun'd args.
    sys.argv = self._args

    # Set context in the process title.
    set_process_title('pantsd-runner [{}]'.format(' '.join(self._args)))

    # Broadcast our process group ID (in PID form - i.e. negated) to the remote client so
    # they can send signals (e.g. SIGINT) to all processes in the runners process group.
    NailgunProtocol.send_pid(self._socket, os.getpid())
    NailgunProtocol.send_pgrp(self._socket, os.getpgrp() * -1)

    # Stop the services that were paused pre-fork.
    for service in self._services.services:
      service.terminate()

    # Invoke a Pants run with stdio redirected and a proxied environment.
    with self.nailgunned_stdio(self._socket, self._env) as finalizer,\
         hermetic_environment_as(**self._env):
      try:
        # Setup the Exiter's finalizer.
        self._exiter.set_finalizer(finalizer)

        # Clean global state.
        clean_global_runtime_state(reset_subsystem=True)

        # Re-raise any deferred exceptions, if present.
        self._raise_deferred_exc()

        # Otherwise, conduct a normal run.
        runner = LocalPantsRunner.create(
          self._exiter,
          self._args,
          self._env,
          self._target_roots,
          self._graph_helper,
          self._options_bootstrapper
        )
        runner.set_start_time(self._maybe_get_client_start_time_from_env(self._env))
        runner.run()
      except KeyboardInterrupt:
        self._exiter.exit_and_fail('Interrupted by user.\n')
      except GracefulTerminationException as e:
        ExceptionSink.log_exception(
          'Encountered graceful termination exception {}; exiting'.format(e))
        self._exiter.exit(e.exit_code)
      except Exception:
        ExceptionSink._log_unhandled_exception_and_exit()
      else:
        self._exiter.exit(0)