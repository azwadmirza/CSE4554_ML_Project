        async def _players_check():
            try:
                get_single_title = lavalink.active_players()[0].current.title
                query = audio_dataclasses.Query.process_input(
                    lavalink.active_players()[0].current.uri
                )
                if get_single_title == "Unknown title":
                    get_single_title = lavalink.active_players()[0].current.uri
                    if not get_single_title.startswith("http"):
                        get_single_title = get_single_title.rsplit("/", 1)[-1]
                elif query.is_local:
                    get_single_title = "{} - {}".format(
                        lavalink.active_players()[0].current.author,
                        lavalink.active_players()[0].current.title,
                    )
                else:
                    get_single_title = lavalink.active_players()[0].current.title
                playing_servers = len(lavalink.active_players())
            except IndexError:
                get_single_title = None
                playing_servers = 0
            return get_single_title, playing_servers