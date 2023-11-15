    async def _build_queue_search_list(queue_list, search_words):
        track_list = []
        queue_idx = 0
        for track in queue_list:
            queue_idx = queue_idx + 1
            if not match_url(track.uri):
                query = audio_dataclasses.Query.process_input(track)
                if track.title == "Unknown title":
                    track_title = query.track.to_string_user()
                else:
                    track_title = "{} - {}".format(track.author, track.title)
            else:
                track_title = track.title

            song_info = {str(queue_idx): track_title}
            track_list.append(song_info)
        search_results = process.extract(search_words, track_list, limit=50)
        search_list = []
        for search, percent_match in search_results:
            for queue_position, title in search.items():
                if percent_match > 89:
                    search_list.append([queue_position, title])
        return search_list