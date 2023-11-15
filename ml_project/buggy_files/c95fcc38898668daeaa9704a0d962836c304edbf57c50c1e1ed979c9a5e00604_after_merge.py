def dispatch_event(event, context):
    error = event.get('detail', {}).get('errorCode')
    if error and C7N_SKIP_EVTERR:
        log.debug("Skipping failed operation: %s" % error)
        return

    if C7N_DEBUG_EVENT:
        event['debug'] = True
        log.info("Processing event\n %s", format_event(event))

    # Policies file should always be valid in lambda so do loading naively
    global policy_config
    if policy_config is None:
        with open('config.json') as f:
            policy_config = json.load(f)

    if not policy_config or not policy_config.get('policies'):
        return False

    options = init_config(policy_config)

    policies = PolicyCollection.from_data(policy_config, options)
    if policies:
        for p in policies:
            try:
                # validation provides for an initialization point for
                # some filters/actions.
                p.validate()
                p.push(event, context)
            except Exception:
                log.exception("error during policy execution")
                if C7N_CATCH_ERR:
                    continue
                raise
    return True