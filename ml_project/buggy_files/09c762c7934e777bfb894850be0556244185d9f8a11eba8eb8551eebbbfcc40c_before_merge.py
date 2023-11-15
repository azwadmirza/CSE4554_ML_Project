    def __init__(self, *args, cli_flags=None, bot_dir: Path = Path.cwd(), **kwargs):
        self._shutdown_mode = ExitCodes.CRITICAL
        self._cli_flags = cli_flags
        self._config = Config.get_core_conf(force_registration=False)
        self._co_owners = cli_flags.co_owner
        self.rpc_enabled = cli_flags.rpc
        self.rpc_port = cli_flags.rpc_port
        self._last_exception = None
        self._config.register_global(
            token=None,
            prefix=[],
            packages=[],
            owner=None,
            whitelist=[],
            blacklist=[],
            locale="en-US",
            embeds=True,
            color=15158332,
            fuzzy=False,
            custom_info=None,
            help__page_char_limit=1000,
            help__max_pages_in_guild=2,
            help__delete_delay=0,
            help__use_menus=False,
            help__show_hidden=False,
            help__verify_checks=True,
            help__verify_exists=False,
            help__tagline="",
            description="Red V3",
            invite_public=False,
            invite_perm=0,
            disabled_commands=[],
            disabled_command_msg="That command is disabled.",
            extra_owner_destinations=[],
            owner_opt_out_list=[],
            last_system_info__python_version=[3, 7],
            last_system_info__machine=None,
            last_system_info__system=None,
            schema_version=0,
        )

        self._config.register_guild(
            prefix=[],
            whitelist=[],
            blacklist=[],
            admin_role=[],
            mod_role=[],
            embeds=None,
            use_bot_color=False,
            fuzzy=False,
            disabled_commands=[],
            autoimmune_ids=[],
        )

        self._config.register_channel(embeds=None)
        self._config.register_user(embeds=None)

        self._config.init_custom(CUSTOM_GROUPS, 2)
        self._config.register_custom(CUSTOM_GROUPS)

        self._config.init_custom(SHARED_API_TOKENS, 2)
        self._config.register_custom(SHARED_API_TOKENS)
        self._prefix_cache = PrefixManager(self._config, cli_flags)

        async def prefix_manager(bot, message) -> List[str]:
            prefixes = await self._prefix_cache.get_prefixes(message.guild)
            if cli_flags.mentionable:
                return when_mentioned_or(*prefixes)(bot, message)
            return prefixes

        if "command_prefix" not in kwargs:
            kwargs["command_prefix"] = prefix_manager

        if cli_flags.owner and "owner_id" not in kwargs:
            kwargs["owner_id"] = cli_flags.owner

        if "command_not_found" not in kwargs:
            kwargs["command_not_found"] = "Command {} not found.\n{}"

        message_cache_size = cli_flags.message_cache_size
        if cli_flags.no_message_cache:
            message_cache_size = None
        kwargs["max_messages"] = message_cache_size
        self._max_messages = message_cache_size

        self._uptime = None
        self._checked_time_accuracy = None
        self._color = discord.Embed.Empty  # This is needed or color ends up 0x000000

        self._main_dir = bot_dir
        self._cog_mgr = CogManager()
        self._use_team_features = cli_flags.use_team_features
        super().__init__(*args, help_command=None, **kwargs)
        # Do not manually use the help formatter attribute here, see `send_help_for`,
        # for a documented API. The internals of this object are still subject to change.
        self._help_formatter = commands.help.RedHelpFormatter()
        self.add_command(commands.help.red_help)

        self._permissions_hooks: List[commands.CheckPredicate] = []
        self._red_ready = asyncio.Event()
        self._red_before_invoke_objs: Set[PreInvokeCoroutine] = set()