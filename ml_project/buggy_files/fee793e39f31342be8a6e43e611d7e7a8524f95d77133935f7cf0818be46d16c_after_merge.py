    def _scrape_episodes(self):
        version = self.config.get("version", "subbed")
        soup = helpers.soupify(helpers.get(self.url))
        ep_list = [x for x in soup.select("div.col-sm-6") if x.find("h5").text == version.title()][0].find_all("a")
        episodes = [x.get("href") for x in ep_list]

        if len(episodes) == 0:
            logger.warning("No episodes found")

        return episodes[::-1]