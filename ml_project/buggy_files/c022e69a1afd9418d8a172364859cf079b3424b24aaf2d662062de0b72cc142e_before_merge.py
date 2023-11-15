def paint_staged_stake_division(emitter,
                                stakeholder,
                                original_stake,
                                target_value,
                                extension):
    new_end_period = original_stake.end_period + extension
    new_duration_periods = new_end_period - original_stake.start_period
    staking_address = original_stake.owner_address

    division_message = f"""
Staking address: {staking_address}
~ Original Stake: {prettify_stake(stake=original_stake, index=None)}
"""

    paint_staged_stake(emitter=emitter,
                       stakeholder=stakeholder,
                       staking_address=staking_address,
                       stake_value=target_value,
                       lock_periods=new_duration_periods,
                       start_period=original_stake.start_period,
                       unlock_period=new_end_period,
                       division_message=division_message)