    async def _build_local_search_list(to_search, search_words):
        to_search_string = {i.track.name for i in to_search}
        search_results = process.extract(search_words, to_search_string, limit=50)
        search_list = []
        for track_match, percent_match in search_results:
            if percent_match > 60:
                search_list.extend(
                    [i.track.to_string_hidden() for i in to_search if i.track.name == track_match]
                )
        return search_list