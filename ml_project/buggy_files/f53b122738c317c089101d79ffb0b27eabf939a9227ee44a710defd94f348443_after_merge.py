    def _execute(cls, all_action_groups):
        with signal_handler(conda_signal_handler), time_recorder("unlink_link_execute"):
            pkg_idx = 0
            try:
                with Spinner("Executing transaction", not context.verbosity and not context.quiet,
                             context.json):
                    for pkg_idx, axngroup in enumerate(all_action_groups):
                        cls._execute_actions(pkg_idx, axngroup)
            except CondaMultiError as e:
                action, is_unlink = (None, axngroup.type == 'unlink')
                prec = axngroup.pkg_data

                log.error("An error occurred while %s package '%s'.\n"
                          "%r\n"
                          "Attempting to roll back.\n",
                          'uninstalling' if is_unlink else 'installing',
                          prec and prec.dist_str(), e.errors[0])

                # reverse all executed packages except the one that failed
                rollback_excs = []
                if context.rollback_enabled:
                    with Spinner("Rolling back transaction",
                                 not context.verbosity and not context.quiet, context.json):
                        failed_pkg_idx = pkg_idx
                        reverse_actions = reversed(tuple(enumerate(
                            take(failed_pkg_idx, all_action_groups)
                        )))
                        for pkg_idx, axngroup in reverse_actions:
                            excs = cls._reverse_actions(pkg_idx, axngroup)
                            rollback_excs.extend(excs)

                raise CondaMultiError(tuple(concatv(
                    (e.errors
                     if isinstance(e, CondaMultiError)
                     else (e,)),
                    rollback_excs,
                )))
            else:
                for axngroup in all_action_groups:
                    for action in axngroup.actions:
                        action.cleanup()