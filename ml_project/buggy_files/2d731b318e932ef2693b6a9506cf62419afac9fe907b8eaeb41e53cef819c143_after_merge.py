async def clear_react(bot: Red, message: discord.Message, emoji: MutableMapping = None) -> None:
    try:
        await message.clear_reactions()
    except discord.Forbidden:
        if not emoji:
            return
        with contextlib.suppress(discord.HTTPException):
            for key in emoji.values():
                await asyncio.sleep(0.2)
                await message.remove_reaction(key, bot.user)
    except discord.HTTPException:
        return