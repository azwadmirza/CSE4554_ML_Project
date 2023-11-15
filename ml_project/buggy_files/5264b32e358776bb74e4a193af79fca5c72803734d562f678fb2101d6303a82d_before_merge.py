def set_min_rate(general_config: GroupGeneralConfig,
                 transacting_staker_options: TransactingStakerOptions,
                 config_file, force, min_rate):
    """Staker sets the minimum acceptable fee rate for their associated worker."""

    # Setup
    emitter = setup_emitter(general_config)
    STAKEHOLDER = transacting_staker_options.create_character(emitter, config_file)
    blockchain = transacting_staker_options.get_blockchain()

    client_account, staking_address = select_client_account_for_staking(
        emitter=emitter,
        stakeholder=STAKEHOLDER,
        staking_address=transacting_staker_options.staker_options.staking_address,
        individual_allocation=STAKEHOLDER.individual_allocation,
        force=force)

    if not min_rate:
        paint_min_rate(emitter, STAKEHOLDER.registry, STAKEHOLDER.policy_agent, staking_address)
        # TODO check range
        min_rate = click.prompt(PROMPT_STAKER_MIN_POLICY_RATE, type=WEI)
    if not force:
        click.confirm(CONFIRM_NEW_MIN_POLICY_RATE.format(min_rate=min_rate), abort=True)
    password = get_password(stakeholder=STAKEHOLDER,
                            blockchain=blockchain,
                            client_account=client_account,
                            hw_wallet=transacting_staker_options.hw_wallet)
    STAKEHOLDER.assimilate(password=password)
    receipt = STAKEHOLDER.set_min_fee_rate(min_rate=min_rate)

    # Report Success
    message = SUCCESSFUL_SET_MIN_POLICY_RATE.format(min_rate=min_rate, staking_address=staking_address)
    emitter.echo(message, color='green')
    paint_receipt_summary(emitter=emitter,
                          receipt=receipt,
                          chain_name=blockchain.client.chain_name,
                          transaction_type='set_min_rate')