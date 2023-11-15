    async def imgur_search(self, ctx, *, term: str):
        """Searches Imgur for the specified term and returns up to 3 results"""
        url = self.imgur_base_url + "time/all/0"
        params = {"q": term}
        headers = {"Authorization": "Client-ID {}".format(await self.settings.imgur_client_id())}
        async with self.session.get(url, headers=headers, data=params) as search_get:
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