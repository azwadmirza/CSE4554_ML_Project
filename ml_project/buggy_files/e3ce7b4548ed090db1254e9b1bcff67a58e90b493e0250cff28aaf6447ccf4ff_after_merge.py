def get_command_from_input(bot, userinput: str):
    com = None
    orig = userinput
    while com is None:
        com = bot.get_command(userinput)
        if com is None:
            userinput = " ".join(userinput.split(" ")[:-1])
        if len(userinput) == 0:
            break
    if com is None:
        return None, _("I could not find a command from that input!")

    if com.requires.privilege_level >= PrivilegeLevel.BOT_OWNER:
        return (
            None,
            _("That command requires bot owner. I can't allow you to use that for an action"),
        )
    return "{prefix}" + orig, None