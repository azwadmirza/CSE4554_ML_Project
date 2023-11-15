async def set_balance(member: discord.Member, amount: int) -> int:
    """Set an account balance.

    Parameters
    ----------
    member : discord.Member
        The member whose balance to set.
    amount : int
        The amount to set the balance to.

    Returns
    -------
    int
        New account balance.

    Raises
    ------
    ValueError
        If attempting to set the balance to a negative number.
    BalanceTooHigh
        If attempting to set the balance to a value greater than
        ``bank.MAX_BALANCE``

    """
    if amount < 0:
        raise ValueError("Not allowed to have negative balance.")
    if amount > MAX_BALANCE:
        currency = (
            await get_currency_name()
            if await is_global()
            else await get_currency_name(member.guild)
        )
        raise errors.BalanceTooHigh(
            user=member.display_name, max_balance=MAX_BALANCE, currency_name=currency
        )
    if await is_global():
        group = _conf.user(member)
    else:
        group = _conf.member(member)
    await group.balance.set(amount)

    if await group.created_at() == 0:
        time = _encoded_current_time()
        await group.created_at.set(time)

    if await group.name() == "":
        await group.name.set(member.display_name)

    return amount