    async def initialize(self):
        await self.bot.wait_until_ready()
        # Unlike most cases, we want the cache to exit before migration.
        await self.music_cache.initialize(self.config)
        await self._migrate_config(
            from_version=await self.config.schema_version(), to_version=_SCHEMA_VERSION
        )
        pass_config_to_dependencies(self.config, self.bot, await self.config.localpath())
        self._restart_connect()
        self._disconnect_task = self.bot.loop.create_task(self.disconnect_timer())
        lavalink.register_event_listener(self.event_handler)
        if not HAS_SQL:
            error_message = (
                "Audio version: {version}\nThis version requires some SQL dependencies to "
                "access the caching features, "
                "your Python install is missing some of them.\n\n"
                "For instructions on how to fix it Google "
                f"`{_ERROR}`.\n"
                "You will need to install the missing SQL dependency.\n\n"
            ).format(version=__version__)
            with contextlib.suppress(discord.HTTPException):
                for page in pagify(error_message):
                    await self.bot.send_to_owners(page)
            log.critical(error_message)

        self._ready_event.set()
        self.bot.dispatch("red_audio_initialized", self)