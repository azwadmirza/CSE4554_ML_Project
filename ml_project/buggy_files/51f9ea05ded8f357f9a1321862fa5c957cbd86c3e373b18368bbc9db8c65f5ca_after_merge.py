def divide(click_config,

           # Stake Options
           poa, light, registry_filepath, config_file, provider_uri, staking_address, hw_wallet,
           beneficiary_address, allocation_filepath,

           # Other
           force, value, lock_periods, index):
    """
    Create a new stake from part of an existing one.
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

    client_account, staking_address = handle_client_account_for_staking(emitter=emitter,
                                                                        stakeholder=STAKEHOLDER,
                                                                        staking_address=staking_address,
                                                                        individual_allocation=STAKEHOLDER.individual_allocation,
                                                                        force=force)

    economics = STAKEHOLDER.economics

    # Dynamic click types (Economics)
    min_locked = economics.minimum_allowed_locked
    stake_value_range = click.FloatRange(min=NU.from_nunits(min_locked).to_tokens(), clamp=False)
    stake_extension_range = click.IntRange(min=1, max=economics.maximum_allowed_locked, clamp=False)

    if staking_address and index is not None:  # 0 is valid.
        STAKEHOLDER.stakes = StakeList(registry=STAKEHOLDER.registry, checksum_address=staking_address)
        STAKEHOLDER.stakes.refresh()
        current_stake = STAKEHOLDER.stakes[index]
    else:
        current_stake = select_stake(stakeholder=STAKEHOLDER, emitter=emitter)

    #
    # Stage Stake
    #

    # Value
    if not value:
        value = click.prompt(f"Enter target value"
                             f"{NU.from_nunits(STAKEHOLDER.economics.minimum_allowed_locked)})"
                             f"- ({str(current_stake.value)}",
                             type=stake_value_range)
    value = NU(value, 'NU')

    # Duration
    if not lock_periods:
        extension = click.prompt("Enter number of periods to extend", type=stake_extension_range)
    else:
        extension = lock_periods

    if not force:
        painting.paint_staged_stake_division(emitter=emitter,
                                             stakeholder=STAKEHOLDER,
                                             original_stake=current_stake,
                                             target_value=value,
                                             extension=extension)
        click.confirm("Is this correct?", abort=True)

    # Execute
    password = None
    if not hw_wallet and not blockchain.client.is_local:
        password = get_client_password(checksum_address=current_stake.staker_address)

    STAKEHOLDER.assimilate(checksum_address=current_stake.staker_address, password=password)
    modified_stake, new_stake = STAKEHOLDER.divide_stake(stake_index=current_stake.index,
                                                         target_value=value,
                                                         additional_periods=extension)
    emitter.echo('Successfully divided stake', color='green', verbosity=1)
    paint_receipt_summary(emitter=emitter,
                          receipt=new_stake.receipt,
                          chain_name=blockchain.client.chain_name)

    # Show the resulting stake list
    painting.paint_stakes(emitter=emitter, stakes=STAKEHOLDER.stakes)