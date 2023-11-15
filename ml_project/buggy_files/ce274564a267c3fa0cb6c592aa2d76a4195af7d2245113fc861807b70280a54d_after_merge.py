def paint_stakes(emitter, stakes, paint_inactive: bool = False):
    header = f'| ~ | Staker | Worker | # | Value    | Duration     | Enactment          '
    breaky = f'|   | ------ | ------ | - | -------- | ------------ | ----------------------------------------- '

    active_stakes = sorted((stake for stake in stakes if stake.is_active),
                           key=lambda some_stake: some_stake.address_index_ordering_key)
    if active_stakes:
        title = "======================================= Active Stakes =========================================\n"
        emitter.echo(title)
        emitter.echo(header, bold=True)
        emitter.echo(breaky, bold=True)

        for index, stake in enumerate(active_stakes):
            row = prettify_stake(stake=stake, index=index)
            row_color = 'yellow' if stake.worker_address == BlockchainInterface.NULL_ADDRESS else 'white'
            emitter.echo(row, color=row_color)
        emitter.echo('')  # newline

    if paint_inactive:
        title = "\n====================================== Inactive Stakes ========================================\n"
        emitter.echo(title)
        emitter.echo(header, bold=True)
        emitter.echo(breaky, bold=True)

        for stake in sorted([s for s in stakes if s not in active_stakes],  # TODO
                            key=lambda some_stake: some_stake.address_index_ordering_key):
            row = prettify_stake(stake=stake, index=None)
            emitter.echo(row, color='red')

        emitter.echo('')  # newline
    elif not active_stakes:
        emitter.echo(f"There are no active stakes\n")