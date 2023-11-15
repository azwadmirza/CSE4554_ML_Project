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

    """
    if amount < 0:
        raise ValueError("Not allowed to have negative balance.")
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