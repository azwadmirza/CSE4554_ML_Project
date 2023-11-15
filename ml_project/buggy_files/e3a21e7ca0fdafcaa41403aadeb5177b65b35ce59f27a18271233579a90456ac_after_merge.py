async def remove_react(message, react_emoji, react_user) -> None:
    with contextlib.suppress(discord.HTTPException):
        await message.remove_reaction(react_emoji, react_user)