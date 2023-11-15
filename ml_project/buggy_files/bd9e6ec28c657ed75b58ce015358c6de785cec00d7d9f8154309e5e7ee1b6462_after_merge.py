    async def imgur_search(self, ctx, *, term: str):
        """Searches Imgur for the specified term and returns up to 3 results"""
        url = self.imgur_base_url + "gallery/search/time/all/0"
        params = {"q": term}
        imgur_client_id = await self.settings.imgur_client_id()
        if not imgur_client_id:
            await ctx.send(
                _("A client ID has not been set! Please set one with {}").format(
                    "`{}imgurcreds`".format(ctx.prefix)))
            return
        headers = {"Authorization": "Client-ID {}".format(imgur_client_id)}
        async with self.session.get(url, headers=headers, params=params) as search_get:
            data = await search_get.json()

        if data["success"]:
            results = data["data"]
            if not results:
                await ctx.send(_("Your search returned no results"))
                return
            shuffle(results)
            msg = _("Search results...\n")
            for r in results[:3]:
                msg += r["gifv"] if "gifv" in r else r["link"]
                msg += "\n"
            await ctx.send(msg)
        else:
            await ctx.send(_("Something went wrong. Error code is {}").format(data["status"]))