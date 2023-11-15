    async def localpath(self, ctx: commands.Context, *, local_path=None):
        """Set the localtracks path if the Lavalink.jar is not run from the Audio data folder.

        Leave the path blank to reset the path to the default, the Audio data directory.
        """

        if not local_path:
            await self.config.localpath.set(str(cog_data_path(raw_name="Audio")))
            pass_config_to_dependencies(
                self.config, self.bot, str(cog_data_path(raw_name="Audio"))
            )
            return await self._embed_msg(
                ctx, _("The localtracks path location has been reset to the default location.")
            )

        info_msg = _(
            "This setting is only for bot owners to set a localtracks folder location "
            "In the example below, the full path for 'ParentDirectory' "
            "must be passed to this command.\n"
            "The path must not contain spaces.\n"
            "```\n"
            "ParentDirectory\n"
            "  |__ localtracks  (folder)\n"
            "  |     |__ Awesome Album Name  (folder)\n"
            "  |           |__01 Cool Song.mp3\n"
            "  |           |__02 Groovy Song.mp3\n"
            "```\n"
            "The folder path given to this command must contain the localtracks folder.\n"
            "**This folder and files need to be visible to the user where `"
            "Lavalink.jar` is being run from.**\n"
            "Use this command with no path given to reset it to the default, "
            "the Audio data directory for this bot.\n"
            "Do you want to continue to set the provided path for local tracks?"
        )
        info = await ctx.maybe_send_embed(info_msg)

        start_adding_reactions(info, ReactionPredicate.YES_OR_NO_EMOJIS)
        pred = ReactionPredicate.yes_or_no(info, ctx.author)
        await ctx.bot.wait_for("reaction_add", check=pred)

        if not pred.result:
            with contextlib.suppress(discord.HTTPException):
                await info.delete()
            return
        temp = audio_dataclasses.LocalPath(local_path, forced=True)
        if not temp.exists() or not temp.is_dir():
            return await self._embed_msg(
                ctx,
                _("{local_path} does not seem like a valid path.").format(local_path=local_path),
            )

        if not temp.localtrack_folder.exists():
            warn_msg = _(
                "`{localtracks}` does not exist. "
                "The path will still be saved, but please check the path and "
                "create a localtracks folder in `{localfolder}` before attempting "
                "to play local tracks."
            ).format(localfolder=temp.absolute(), localtracks=temp.localtrack_folder.absolute())
            await ctx.send(
                embed=discord.Embed(
                    title=_("Incorrect environment."),
                    description=warn_msg,
                    colour=await ctx.embed_colour(),
                )
            )
        local_path = str(temp.localtrack_folder.absolute())
        await self.config.localpath.set(local_path)
        pass_config_to_dependencies(self.config, self.bot, local_path)
        await self._embed_msg(
            ctx, _("Localtracks path set to: {local_path}.").format(local_path=local_path)
        )