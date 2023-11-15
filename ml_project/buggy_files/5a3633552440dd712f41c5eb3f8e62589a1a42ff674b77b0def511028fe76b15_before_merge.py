    def search(cls, query):
        results = helpers.get("https://dreamanime.fun/search", params = {"term" : query}).text
        soup = helpers.soupify(results)
        result_data = soup.find_all("a", {"id":"epilink"})

        search_results = [
            SearchResult(
                title = result.text,
                url = result.get("href")
                )
            for result in result_data
            ]

        return search_results