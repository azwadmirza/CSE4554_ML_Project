def create(click_config,

           # Stake Options
           poa, light, registry_filepath, config_file, provider_uri, staking_address, hw_wallet,
           beneficiary_address, allocation_filepath,

           # Other
           force, value, lock_periods):
    """
    Initialize a new stake.
    """

    ### Setup ###
    emitter = _setup_emitter(click_config)

    STAKEHOLDER, blockchain = _create_stakeholder(config_file,
                                                  provider_uri,
                                                  poa,
                                                  light,
                                                  registry_filepath,
                                                  staking_address,
                                                  beneficiary_address=beneficiary_address,
                                                  allocation_filepath=allocation_filepath)
    #############

    economics = STAKEHOLDER.economics

    client_account, staking_address = handle_client_account_for_staking(emitter=emitter,
                                                                        stakeholder=STAKEHOLDER,
                                                                        staking_address=staking_address,
                                                                        individual_allocation=STAKEHOLDER.individual_allocation,
                                                                        force=force)

    # Dynamic click types (Economics)
    min_locked = economics.minimum_allowed_locked
    stake_value_range = click.FloatRange(min=NU.from_nunits(min_locked).to_tokens(), clamp=False)
    stake_duration_range = click.IntRange(min=economics.minimum_locked_periods, clamp=False)

    password = None
    if not hw_wallet and not blockchain.client.is_local:
        password = get_client_password(checksum_address=client_account)

    #
    # Stage Stake
    #

    if not value:
        value = click.prompt(f"Enter stake value in NU "
                             f"({NU.from_nunits(STAKEHOLDER.economics.minimum_allowed_locked)} - "
                             f"{NU.from_nunits(STAKEHOLDER.economics.maximum_allowed_locked)})",
                             type=stake_value_range,
                             default=NU.from_nunits(min_locked).to_tokens())
    value = NU.from_tokens(value)

    if not lock_periods:
        prompt = f"Enter stake duration ({STAKEHOLDER.economics.minimum_locked_periods} periods minimum)"
        lock_periods = click.prompt(prompt, type=stake_duration_range)

    start_period = STAKEHOLDER.staking_agent.get_current_period() + 1
    unlock_period = start_period + lock_periods

    #
    # Review
    #

    if not force:
        painting.paint_staged_stake(emitter=emitter,
                                    stakeholder=STAKEHOLDER,
                                    staking_address=staking_address,
                                    stake_value=value,
                                    lock_periods=lock_periods,
                                    start_period=start_period,
                                    unlock_period=unlock_period)

        confirm_staged_stake(staker_address=staking_address, value=value, lock_periods=lock_periods)

    # Last chance to bail
    click.confirm("Publish staged stake to the blockchain?", abort=True)

    # Execute
    STAKEHOLDER.assimilate(checksum_address=client_account, password=password)
    new_stake = STAKEHOLDER.initialize_stake(amount=value, lock_periods=lock_periods)

    painting.paint_staking_confirmation(emitter=emitter,
                                        ursula=STAKEHOLDER,
                                        transactions=new_stake.transactions)