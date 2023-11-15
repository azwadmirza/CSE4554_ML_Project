    def search(cls, query):
        soup = helpers.soupify(helpers.get("https://dreamanime.fun/search", params = {"term" : query}))
        result_data = soup.select("a#epilink")

        search_results = [
            SearchResult(
                title = result.text,
                url = result.get("href")
                )
            for result in result_data
            ]

        return search_results