def confirm_activity(click_config,

                     # API Options
                     geth, provider_uri, network, registry_filepath, staker_address, worker_address, federated_only,
                     rest_host, rest_port, db_filepath, poa, light, config_file, dev, lonely, teacher_uri, min_stake):
    """
    Manually confirm-activity for the current period.
    """

    ### Setup ###
    _validate_args(geth, federated_only, staker_address, registry_filepath)

    emitter = _setup_emitter(click_config, worker_address)

    _pre_launch_warnings(emitter, dev=dev, force=None)

    ursula_config, provider_uri = _get_ursula_config(emitter, geth, provider_uri, network, registry_filepath, dev,
                                                     config_file, staker_address, worker_address, federated_only,
                                                     rest_host, rest_port, db_filepath, poa, light)
    #############

    URSULA = _create_ursula(ursula_config, click_config, dev, emitter,
                            lonely, teacher_uri, min_stake, load_seednodes=False)

    confirmed_period = URSULA.staking_agent.get_current_period() + 1
    click.echo(f"Confirming activity for period {confirmed_period}", color='blue')
    receipt = URSULA.confirm_activity()

    economics = TokenEconomicsFactory.get_economics(registry=URSULA.registry)
    date = datetime_at_period(period=confirmed_period,
                              seconds_per_period=economics.seconds_per_period)

    # TODO: Double-check dates here
    emitter.echo(f'\nActivity confirmed for period #{confirmed_period} '
                 f'(starting at {date})', bold=True, color='blue')
    painting.paint_receipt_summary(emitter=emitter,
                                   receipt=receipt,
                                   chain_name=URSULA.staking_agent.blockchain.client.chain_name)