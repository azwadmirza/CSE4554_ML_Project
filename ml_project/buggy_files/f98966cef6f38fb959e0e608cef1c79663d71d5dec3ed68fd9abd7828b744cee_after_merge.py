    def __init__(
        self, ctx: commands.Context, message: discord.Message, updates: MutableMapping, **kwargs
    ):
        self.context = ctx
        self.message = message
        self.updates = updates
        self.color = None
        self.last_msg_time = 0
        self.cooldown = 5