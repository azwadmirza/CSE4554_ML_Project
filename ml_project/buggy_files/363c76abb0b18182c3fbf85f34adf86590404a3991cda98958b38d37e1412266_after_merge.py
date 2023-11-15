    async def initialize(self) -> None:
        await self.bot.wait_until_ready()
        # Unlike most cases, we want the cache to exit before migration.
        try:
            pass_config_to_dependencies(self.config, self.bot, await self.config.localpath())
            self.music_cache = MusicCache(self.bot, self.session)
            await self.music_cache.initialize(self.config)
            await self._migrate_config(
                from_version=await self.config.schema_version(), to_version=_SCHEMA_VERSION
            )
            dat = get_playlist_database()
            if dat:
                dat.delete_scheduled()
            self._restart_connect()
            self._disconnect_task = self.bot.loop.create_task(self.disconnect_timer())
            lavalink.register_event_listener(self.event_handler)
        except Exception as err:
            log.exception("Audio failed to start up, please report this issue.", exc_info=err)
            raise err

        self._ready_event.set()