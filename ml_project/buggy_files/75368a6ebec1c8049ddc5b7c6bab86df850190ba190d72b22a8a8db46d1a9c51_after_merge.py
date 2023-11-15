    def lyrics_from_song_api_path(self, song_api_path):
        song_url = self.base_url + song_api_path
        response = requests.get(song_url, headers=self.headers)
        json = response.json()
        path = json["response"]["song"]["path"]

        # Gotta go regular html scraping... come on Genius.
        page_url = "https://genius.com" + path
        page = requests.get(page_url)
        html = BeautifulSoup(page.text, "html.parser")

        # Remove script tags that they put in the middle of the lyrics.
        [h.extract() for h in html('script')]

        # At least Genius is nice and has a tag called 'lyrics'!
        # Updated css where the lyrics are based in HTML.
        lyrics = html.find("div", class_="lyrics").get_text()

        return lyrics