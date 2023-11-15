def _find_domains_or_certname(config, installer):
    """Retrieve domains and certname from config or user input.
    """
    domains = None
    if config.domains:
        domains = config.domains
    elif not config.certname:
        domains = display_ops.choose_names(installer)

    if not domains and not config.certname:
        raise errors.Error("Please specify --domains, or --installer that "
                           "will help in domain names autodiscovery, or "
                           "--cert-name for an existing certificate name.")

    return domains, config.certname