    def _scrape_episodes(self):
        version = self.config.get("version", "subbed")
        soup = helpers.soupify(helpers.get(self.url))

        episodes = []
 
        _all = soup.find_all("div", {"class":"episode-wrap"})
        for i in _all:
            ep_type = i.find("div", {"class":re.compile("ep-type type-.* dscd")}).text
            if ep_type == 'Sub':
                episodes.append(i.find("a").get("data-src"))
            elif ep_type == 'Dub':
                episodes.append(i.find("a").get("href"))
        
        if len(episodes) == 0:
            logger.warning("No episodes found")

        return episodes[::-1]