    def search(cls, query):
        soup = helpers.soupify(helpers.get("https://www4.ryuanime.com/search", params = {"term" : query}))
        result_data = soup.select("ul.list-inline")[0].select("a")

        search_results = [
            SearchResult(
                title = result.text,
                url = result.get("href")
                )
            for result in result_data
            ]
        return search_results