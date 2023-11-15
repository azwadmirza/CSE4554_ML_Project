    async def imgur_subreddit(self, ctx, subreddit: str, sort_type: str="top", window: str="day"):
        """Gets images from the specified subreddit section

        Sort types: new, top
        Time windows: day, week, month, year, all"""
        sort_type = sort_type.lower()
        window = window.lower()

        if sort_type not in ("new", "top"):
            await ctx.send(_("Only 'new' and 'top' are a valid sort type."))
            return
        elif window not in ("day", "week", "month", "year", "all"):
            await ctx.send_help()
            return

        if sort_type == "new":
            sort = "time"
        elif sort_type == "top":
            sort = "top"

        imgur_client_id = await self.settings.imgur_client_id()
        if not imgur_client_id:
            await ctx.send(
                _("A client ID has not been set! Please set one with {}").format(
                    "`{}imgurcreds`".format(ctx.prefix)))
            return

        links = []
        headers = {"Authorization": "Client-ID {}".format(imgur_client_id)}
        url = self.imgur_base_url + "gallery/r/{}/{}/{}/0".format(subreddit, sort, window)

        async with self.session.get(url, headers=headers) as sub_get:
            data = await sub_get.json()

        if data["success"]:
            items = data["data"]
            if items:
                for item in items[:3]:
                    link = item["gifv"] if "gifv" in item else item["link"]
                    links.append("{}\n{}".format(item["title"], link))

                if links:
                    await ctx.send("\n".join(links))
            else:
                await ctx.send(_("No results found."))
        else:
            await ctx.send(_("Something went wrong. Error code is {}").format(data["status"]))