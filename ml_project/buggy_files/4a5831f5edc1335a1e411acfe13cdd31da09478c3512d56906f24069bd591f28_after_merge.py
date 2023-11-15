    def solve_for_transaction(self, deps_modifier=NULL, prune=NULL, ignore_pinned=NULL,
                              force_remove=NULL, force_reinstall=False):
        """Gives an UnlinkLinkTransaction instance that can be used to execute the solution
        on an environment.

        Args:
            deps_modifier (DepsModifier):
                See :meth:`solve_final_state`.
            prune (bool):
                See :meth:`solve_final_state`.
            ignore_pinned (bool):
                See :meth:`solve_final_state`.
            force_remove (bool):
                See :meth:`solve_final_state`.
            force_reinstall (bool):
                See :meth:`solve_for_diff`.

        Returns:
            UnlinkLinkTransaction:

        """
        with Spinner("Solving environment", not context.verbosity and not context.quiet,
                     context.json):
            if self.prefix == context.root_prefix and context.enable_private_envs:
                # This path has the ability to generate a multi-prefix transaction. The basic logic
                # is in the commented out get_install_transaction() function below. Exercised at
                # the integration level in the PrivateEnvIntegrationTests in test_create.py.
                raise NotImplementedError()
            else:
                unlink_precs, link_precs = self.solve_for_diff(deps_modifier, prune, ignore_pinned,
                                                               force_remove, force_reinstall)
                stp = PrefixSetup(self.prefix, unlink_precs, link_precs,
                                  self.specs_to_remove, self.specs_to_add)
                # TODO: Only explicitly requested remove and update specs are being included in
                #   History right now. Do we need to include other categories from the solve?

        if context.notify_outdated_conda:
            conda_newer_spec = MatchSpec('conda >%s' % CONDA_VERSION)
            if not any(conda_newer_spec.match(prec) for prec in link_precs):
                conda_newer_records = sorted(
                    SubdirData.query_all(self.channels, self.subdirs, conda_newer_spec),
                    key=lambda x: VersionOrder(x.version)
                )
                if conda_newer_records:
                    latest_version = conda_newer_records[-1].version
                    print(dedent("""

                    ==> WARNING: A newer version of conda exists. <==
                      current version: %s
                      latest version: %s

                    Please update conda by running

                        $ conda update -n base conda

                    """) % (CONDA_VERSION, latest_version), file=sys.stderr)

        return UnlinkLinkTransaction(stp)