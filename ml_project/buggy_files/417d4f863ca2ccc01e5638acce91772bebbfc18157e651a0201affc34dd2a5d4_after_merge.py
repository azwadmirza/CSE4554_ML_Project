def events(general_config, staker_options, config_file, event_name):
    """See blockchain events associated to a staker"""

    # Setup
    emitter = setup_emitter(general_config)
    STAKEHOLDER = staker_options.create_character(emitter, config_file)

    _client_account, staking_address = select_client_account_for_staking(
        emitter=emitter,
        stakeholder=STAKEHOLDER,
        staking_address=staker_options.staking_address,
        individual_allocation=STAKEHOLDER.individual_allocation,
        force=True)

    title = f" {STAKEHOLDER.staking_agent.contract_name} Events ".center(40, "-")
    emitter.echo(f"\n{title}\n", bold=True, color='green')
    if event_name:
        events = [STAKEHOLDER.staking_agent.contract.events[event_name]]
    else:
        raise click.BadOptionUsage(message="You must specify an event name with --event-name")
        # TODO: Doesn't work for the moment
        # event_names = STAKEHOLDER.staking_agent.events.names
        # events = [STAKEHOLDER.staking_agent.contract.events[e] for e in event_names]
        # events = [e for e in events if 'staker' in e.argument_names]

    for event in events:
        emitter.echo(f"{event.event_name}:", bold=True, color='yellow')
        entries = event.getLogs(fromBlock=0, toBlock='latest', argument_filters={'staker': staking_address})
        for event_record in entries:
            emitter.echo(f"  - {EventRecord(event_record)}")