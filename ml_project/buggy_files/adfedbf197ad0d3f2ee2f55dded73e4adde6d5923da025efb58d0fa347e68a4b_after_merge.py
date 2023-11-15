    def _summary(self):
        is_parallel_child = PARALLEL_ENV_VAR_KEY_PRIVATE in os.environ
        if not is_parallel_child:
            reporter.separator("_", "summary", reporter.Verbosity.QUIET)
        exit_code = 0
        for venv in self.venv_dict.values():
            report = reporter.good
            status = getattr(venv, "status", "undefined")
            if isinstance(status, tox.exception.InterpreterNotFound):
                msg = " {}: {}".format(venv.envconfig.envname, str(status))
                if self.config.option.skip_missing_interpreters == "true":
                    report = reporter.skip
                else:
                    exit_code = 1
                    report = reporter.error
            elif status == "platform mismatch":
                msg = " {}: {} ({!r} does not match {!r})".format(
                    venv.envconfig.envname, str(status), sys.platform, venv.envconfig.platform
                )
                report = reporter.skip
            elif status and status == "ignored failed command":
                msg = "  {}: {}".format(venv.envconfig.envname, str(status))
            elif status and status != "skipped tests":
                msg = "  {}: {}".format(venv.envconfig.envname, str(status))
                report = reporter.error
                exit_code = 1
            else:
                if not status:
                    status = "commands succeeded"
                msg = "  {}: {}".format(venv.envconfig.envname, status)
            if not is_parallel_child:
                report(msg)
        if not exit_code and not is_parallel_child:
            reporter.good("  congratulations :)")
        path = self.config.option.resultjson
        if path:
            if not is_parallel_child:
                self._add_parallel_summaries()
            path = py.path.local(path)
            data = self.resultlog.dumps_json()
            reporter.line("write json report at: {}".format(path))
            path.write(data)
        return exit_code