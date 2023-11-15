    def prepare(self):
        if self._prepared:
            return

        self.transaction_context = {}

        with Spinner("Preparing transaction", not context.verbosity and not context.quiet,
                     context.json):
            for stp in itervalues(self.prefix_setups):
                grps = self._prepare(self.transaction_context, stp.target_prefix,
                                     stp.unlink_precs, stp.link_precs,
                                     stp.remove_specs, stp.update_specs)
                self.prefix_action_groups[stp.target_prefix] = PrefixActionGroup(*grps)

        self._prepared = True