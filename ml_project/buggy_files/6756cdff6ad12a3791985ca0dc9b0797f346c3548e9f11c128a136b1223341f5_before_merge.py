    async def local_play(self, ctx):
        """Play a local track."""
        if not await self._localtracks_check(ctx):
            return
        localtracks_folders = await self._localtracks_folders(ctx)
        if not localtracks_folders:
            return await self._embed_msg(ctx, _("No local track folders found."))
        len_folder_pages = math.ceil(len(localtracks_folders) / 5)
        folder_page_list = []
        for page_num in range(1, len_folder_pages + 1):
            embed = await self._build_search_page(ctx, localtracks_folders, page_num)
            folder_page_list.append(embed)

        async def _local_folder_menu(
            ctx: commands.Context,
            pages: list,
            controls: dict,
            message: discord.Message,
            page: int,
            timeout: float,
            emoji: str,
        ):
            if message:
                await message.delete()
                await self._search_button_action(ctx, localtracks_folders, emoji, page)
                return None

        LOCAL_FOLDER_CONTROLS = {
            "1⃣": _local_folder_menu,
            "2⃣": _local_folder_menu,
            "3⃣": _local_folder_menu,
            "4⃣": _local_folder_menu,
            "5⃣": _local_folder_menu,
            "⬅": prev_page,
            "❌": close_menu,
            "➡": next_page,
        }

        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await menu(ctx, folder_page_list, DEFAULT_CONTROLS)
        else:
            await menu(ctx, folder_page_list, LOCAL_FOLDER_CONTROLS)