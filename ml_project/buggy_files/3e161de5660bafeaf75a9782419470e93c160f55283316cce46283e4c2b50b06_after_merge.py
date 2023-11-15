def paint_min_rate(emitter, staker):
    paint_fee_rate_range(emitter, staker.policy_agent)
    minimum = staker.min_fee_rate
    raw_minimum = staker.raw_min_fee_rate

    rate_payload = f"""
Minimum acceptable fee rate (set by staker for their associated worker):
    ~ Previously set ....... {prettify_eth_amount(raw_minimum)}
    ~ Effective ............ {prettify_eth_amount(minimum)}"""
    emitter.echo(rate_payload)