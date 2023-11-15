    def verify(self):
        if not self._prepared:
            self.prepare()

        assert not context.dry_run

        if context.safety_checks == SafetyChecks.disabled:
            self._verified = True
            return

        with spinner("Verifying transaction", not context.verbosity and not context.quiet,
                     context.json):
            exceptions = self._verify(self.prefix_setups, self.prefix_action_groups)
            if exceptions:
                try:
                    maybe_raise(CondaMultiError(exceptions), context)
                except:
                    rm_rf(self.transaction_context['temp_dir'])
                    raise
                log.info(exceptions)

        self._verified = True