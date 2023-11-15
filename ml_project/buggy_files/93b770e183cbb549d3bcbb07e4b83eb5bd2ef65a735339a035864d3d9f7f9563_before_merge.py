    def search(cls, query):
        results = helpers.get("https://www4.ryuanime.com/search", params = {"term" : query}).text
        soup = helpers.soupify(results)
        result_data = soup.find("ul", {"class" : "list-inline"}).find_all("a")

        search_results = [
            SearchResult(
                title = result.text,
                url = result.get("href")
                )
            for result in result_data
            ]
        return search_results