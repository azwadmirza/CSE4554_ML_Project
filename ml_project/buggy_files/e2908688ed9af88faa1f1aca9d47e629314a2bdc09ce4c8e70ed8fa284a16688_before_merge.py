async def get_case(case_number: int, guild: discord.Guild, bot: Red) -> Case:
    """
    Gets the case with the associated case number

    Parameters
    ----------
    case_number: int
        The case number for the case to get
    guild: discord.Guild
        The guild to get the case from
    bot: Red
        The bot's instance

    Returns
    -------
    Case
        The case associated with the case number

    Raises
    ------
    RuntimeError
        If there is no case for the specified number

    """
    try:
        case = await _conf.custom(_CASES, str(guild.id), str(case_number)).all()
    except KeyError as e:
        raise RuntimeError("That case does not exist for guild {}".format(guild.name)) from e
    mod_channel = await get_modlog_channel(guild)
    return await Case.from_json(mod_channel, bot, case_number, case)