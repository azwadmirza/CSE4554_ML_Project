def paint_min_rate(emitter, registry, policy_agent, staker_address):
    paint_fee_rate_range(emitter, policy_agent)
    minimum = policy_agent.min_fee_rate(staker_address)
    raw_minimum = policy_agent.raw_min_fee_rate(staker_address)

    rate_payload = f"""
Minimum acceptable fee rate (set by staker for their associated worker):
    ~ Previously set ....... {prettify_eth_amount(raw_minimum)}
    ~ Effective ............ {prettify_eth_amount(minimum)}"""
    emitter.echo(rate_payload)