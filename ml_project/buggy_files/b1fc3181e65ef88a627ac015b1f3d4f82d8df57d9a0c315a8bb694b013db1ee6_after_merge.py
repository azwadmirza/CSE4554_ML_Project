    def __init__(
        self,
        bot: Red,
        guild: discord.Guild,
        created_at: int,
        action_type: str,
        user: Union[discord.User, int],
        moderator: Optional[Union[discord.User, int]],
        case_number: int,
        reason: str = None,
        until: int = None,
        channel: Optional[Union[discord.TextChannel, discord.VoiceChannel, int]] = None,
        amended_by: Optional[Union[discord.User, int]] = None,
        modified_at: Optional[int] = None,
        message: Optional[discord.Message] = None,
        last_known_username: Optional[str] = None,
    ):
        self.bot = bot
        self.guild = guild
        self.created_at = created_at
        self.action_type = action_type
        self.user = user
        self.last_known_username = last_known_username
        self.moderator = moderator
        self.reason = reason
        self.until = until
        self.channel = channel
        self.amended_by = amended_by
        self.modified_at = modified_at
        self.case_number = case_number
        self.message = message