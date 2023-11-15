def set_worker(click_config,

               # Worker Options
               poa, light, registry_filepath, config_file, provider_uri, staking_address, hw_wallet,
               beneficiary_address, allocation_filepath,
               worker_address, 
               
               # Other options
               force):
    """
    Bond a worker to a staker.
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

    if not worker_address:
        worker_address = click.prompt("Enter worker address", type=EIP55_CHECKSUM_ADDRESS)

    # TODO: Check preconditions (e.g., minWorkerPeriods, already in use, etc)

    password = None
    if not hw_wallet and not blockchain.client.is_local:
        password = get_client_password(checksum_address=client_account)

    # TODO: Double-check dates
    # Calculate release datetime
    current_period = STAKEHOLDER.staking_agent.get_current_period()
    bonded_date = datetime_at_period(period=current_period, seconds_per_period=economics.seconds_per_period)
    min_worker_periods = STAKEHOLDER.economics.minimum_worker_periods
    release_period = current_period + min_worker_periods
    release_date = datetime_at_period(period=release_period,
                                      seconds_per_period=economics.seconds_per_period,
                                      start_of_period=True)

    click.confirm(f"Commit to bonding "
                  f"worker {worker_address} to staker {client_account} "
                  f"for a minimum of {STAKEHOLDER.economics.minimum_worker_periods} periods?", abort=True)

    STAKEHOLDER.assimilate(checksum_address=client_account, password=password)
    receipt = STAKEHOLDER.set_worker(worker_address=worker_address)

    # Report Success
    emitter.echo(f"\nWorker {worker_address} successfully bonded to staker {staking_address}", color='green')
    paint_receipt_summary(emitter=emitter,
                          receipt=receipt,
                          chain_name=blockchain.client.chain_name,
                          transaction_type='set_worker')
    emitter.echo(f"Bonded at period #{current_period} ({bonded_date})", color='green')
    emitter.echo(f"This worker can be replaced or detached after period "
                 f"#{release_period} ({release_date})", color='green')