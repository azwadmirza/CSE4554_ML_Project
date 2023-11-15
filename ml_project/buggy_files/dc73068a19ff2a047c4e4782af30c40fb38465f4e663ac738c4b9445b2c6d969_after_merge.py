    async def from_json(
        cls, mod_channel: discord.TextChannel, bot: Red, case_number: int, data: dict, **kwargs
    ):
        """Get a Case object from the provided information

        Parameters
        ----------
        mod_channel: discord.TextChannel
            The mod log channel for the guild
        bot: Red
            The bot's instance. Needed to get the target user
        case_number: int
            The case's number.
        data: dict
            The JSON representation of the case to be gotten
        **kwargs
            Extra attributes for the Case instance which override values
            in the data dict. These should be complete objects and not
            IDs, where possible.

        Returns
        -------
        Case
            The case object for the requested case

        Raises
        ------
        `discord.NotFound`
            The user the case is for no longer exists
        `discord.Forbidden`
            Cannot read message history to fetch the original message.
        `discord.HTTPException`
            A generic API issue
        """
        guild = kwargs.get("guild") or mod_channel.guild

        message = kwargs.get("message")
        if message is None:
            message_id = data.get("message")
            if message_id is not None:
                try:
                    message = discord.utils.get(bot.cached_messages, id=message_id)
                except AttributeError:
                    # bot.cached_messages didn't exist prior to discord.py 1.1.0
                    message = None
                if message is None:
                    try:
                        message = await mod_channel.fetch_message(message_id)
                    except (discord.HTTPException, AttributeError):
                        message = None
            else:
                message = None

        user_objects = {"user": None, "moderator": None, "amended_by": None}
        for user_key in tuple(user_objects):
            user_object = kwargs.get(user_key)
            if user_object is None:
                user_id = data.get(user_key)
                if user_id is None:
                    user_object = None
                else:
                    user_object = bot.get_user(user_id) or user_id
            user_objects[user_key] = user_object

        channel = kwargs.get("channel") or guild.get_channel(data["channel"]) or data["channel"]
        case_guild = kwargs.get("guild") or bot.get_guild(data["guild"])
        return cls(
            bot=bot,
            guild=case_guild,
            created_at=data["created_at"],
            action_type=data["action_type"],
            case_number=case_number,
            reason=data["reason"],
            until=data["until"],
            channel=channel,
            modified_at=data["modified_at"],
            message=message,
            last_known_username=data.get("last_known_username"),
            **user_objects,
        )