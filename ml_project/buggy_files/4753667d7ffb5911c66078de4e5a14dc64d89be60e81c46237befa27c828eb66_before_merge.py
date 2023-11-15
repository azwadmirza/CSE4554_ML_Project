    async def _genre_search_button_action(
        ctx: commands.Context, options, emoji, page, playlist=False
    ):
        try:
            if emoji == "1⃣":
                search_choice = options[0 + (page * 5)]
            elif emoji == "2⃣":
                search_choice = options[1 + (page * 5)]
            elif emoji == "3⃣":
                search_choice = options[2 + (page * 5)]
            elif emoji == "4⃣":
                search_choice = options[3 + (page * 5)]
            elif emoji == "5⃣":
                search_choice = options[4 + (page * 5)]
            else:
                search_choice = options[0 + (page * 5)]
                # TODO: Verify this doesn't break exit and arrows
        except IndexError:
            search_choice = options[-1]
        if not playlist:
            return list(search_choice.items())[0]
        else:
            return search_choice.get("uri")