async def mass_purge(messages: List[discord.Message], channel: discord.TextChannel):
    """Bulk delete messages from a channel.

    If more than 100 messages are supplied, the bot will delete 100 messages at
    a time, sleeping between each action.

    Note
    ----
    Messages must not be older than 14 days, and the bot must not be a user
    account.

    Parameters
    ----------
    messages : `list` of `discord.Message`
        The messages to bulk delete.
    channel : discord.TextChannel
        The channel to delete messages from.

    Raises
    ------
    discord.Forbidden
        You do not have proper permissions to delete the messages or you’re not
        using a bot account.
    discord.HTTPException
        Deleting the messages failed.

    """
    while messages:
        if len(messages) > 1:
            await channel.delete_messages(messages[:100])
            messages = messages[100:]
        else:
            await messages[0].delete()
            messages = []
        await asyncio.sleep(1.5)