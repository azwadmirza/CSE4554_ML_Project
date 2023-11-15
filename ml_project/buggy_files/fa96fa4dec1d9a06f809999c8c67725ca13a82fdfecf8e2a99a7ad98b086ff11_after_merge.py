    async def _players_check():
        try:
            current = next(
                (
                    player.current
                    for player in lavalink.active_players()
                    if player.current is not None
                ),
                None,
            )
            get_single_title = get_track_description_unformatted(current)
            playing_servers = len(lavalink.active_players())
        except IndexError:
            get_single_title = None
            playing_servers = 0
        return get_single_title, playing_servers