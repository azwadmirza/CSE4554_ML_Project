def renew_all_lineages(config):
    """Examine each lineage; renew if due and report results"""

    if config.domains != []:
        raise errors.Error("Currently, the renew verb is only capable of "
                           "renewing all installed certificates that are due "
                           "to be renewed; individual domains cannot be "
                           "specified with this action. If you would like to "
                           "renew specific certificates, use the certonly "
                           "command. The renew verb may provide other options "
                           "for selecting certificates to renew in the future.")
    renewer_config = configuration.RenewerConfiguration(config)
    renew_successes = []
    renew_failures = []
    renew_skipped = []
    parse_failures = []
    for renewal_file in renewal_conf_files(renewer_config):
        disp = zope.component.getUtility(interfaces.IDisplay)
        disp.notification("Processing " + renewal_file, pause=False)
        lineage_config = copy.deepcopy(config)

        # Note that this modifies config (to add back the configuration
        # elements from within the renewal configuration file).
        try:
            renewal_candidate = _reconstitute(lineage_config, renewal_file)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Renewal configuration file %s produced an "
                           "unexpected error: %s. Skipping.", renewal_file, e)
            logger.debug("Traceback was:\n%s", traceback.format_exc())
            parse_failures.append(renewal_file)
            continue

        try:
            if renewal_candidate is None:
                parse_failures.append(renewal_file)
            else:
                # XXX: ensure that each call here replaces the previous one
                zope.component.provideUtility(lineage_config)
                if should_renew(lineage_config, renewal_candidate):
                    plugins = plugins_disco.PluginsRegistry.find_all()
                    from certbot import main
                    main.obtain_cert(lineage_config, plugins, renewal_candidate)
                    renew_successes.append(renewal_candidate.fullchain)
                else:
                    renew_skipped.append(renewal_candidate.fullchain)
        except Exception as e:  # pylint: disable=broad-except
            # obtain_cert (presumably) encountered an unanticipated problem.
            logger.warning("Attempting to renew cert from %s produced an "
                           "unexpected error: %s. Skipping.", renewal_file, e)
            logger.debug("Traceback was:\n%s", traceback.format_exc())
            renew_failures.append(renewal_candidate.fullchain)

    # Describe all the results
    _renew_describe_results(config, renew_successes, renew_failures,
                            renew_skipped, parse_failures)

    if renew_failures or parse_failures:
        raise errors.Error("{0} renew failure(s), {1} parse failure(s)".format(
            len(renew_failures), len(parse_failures)))
    else:
        logger.debug("no renewal failures")