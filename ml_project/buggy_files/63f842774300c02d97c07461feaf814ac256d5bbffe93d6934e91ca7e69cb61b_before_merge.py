    async def _playlist_list(self, ctx):
        """List saved playlists."""
        playlists = await self.config.guild(ctx.guild).playlists.get_raw()
        if not playlists:
            return await self._embed_msg(ctx, _("No saved playlists."))
        playlist_list = []
        space = "\N{EN SPACE}"
        for playlist_name in playlists:
            tracks = playlists[playlist_name]["tracks"]
            if not tracks:
                tracks = []
            author = playlists[playlist_name]["author"]
            playlist_list.append(
                ("\n" + space * 4).join(
                    (
                        bold(playlist_name),
                        _("Tracks: {num}").format(num=len(tracks)),
                        _("Author: {name}").format(self.bot.get_user(author)),
                    )
                )
            )
        abc_names = sorted(playlist_list, key=str.lower)
        len_playlist_list_pages = math.ceil(len(abc_names) / 5)
        playlist_embeds = []
        for page_num in range(1, len_playlist_list_pages + 1):
            embed = await self._build_playlist_list_page(ctx, page_num, abc_names)
            playlist_embeds.append(embed)
        await menu(ctx, playlist_embeds, DEFAULT_CONTROLS)