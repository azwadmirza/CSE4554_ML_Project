    async def restrict(self, ctx: commands.Context):
        """Toggle the domain restriction on Audio.

        When toggled off, users will be able to play songs from non-commercial websites and links.
        When toggled on, users are restricted to YouTube, SoundCloud, Mixer, Vimeo, Twitch, and
        Bandcamp links.
        """
        restrict = await self.config.restrict()
        await self.config.restrict.set(not restrict)
        await self._embed_msg(
            ctx,
            title=_("Setting Changed"),
            description=_("Commercial links only: {true_or_false}.").format(
                true_or_false=_("Enabled") if not restrict else _("Disabled")
            ),
        )