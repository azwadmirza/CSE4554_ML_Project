    async def _maybe_update_playlist(
        self, ctx: commands.Context, player: lavalink.player_manager.Player, playlist: Playlist
    ) -> Tuple[List[lavalink.Track], List[lavalink.Track], Playlist]:
        if playlist.url is None:
            return [], [], playlist
        results = {}
        updated_tracks = await self._playlist_tracks(
            ctx, player, audio_dataclasses.Query.process_input(playlist.url)
        )
        if not updated_tracks:
            # No Tracks available on url Lets set it to none to avoid repeated calls here
            results["url"] = None
        if updated_tracks:  # Tracks have been updated
            results["tracks"] = updated_tracks

        old_tracks = playlist.tracks_obj
        new_tracks = [lavalink.Track(data=track) for track in updated_tracks]
        removed = list(set(old_tracks) - set(new_tracks))
        added = list(set(new_tracks) - set(old_tracks))
        if removed or added:
            await playlist.edit(results)

        return added, removed, playlist