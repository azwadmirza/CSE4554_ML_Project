    def fetch_popular_shows(self):
        """Get popular show information from IMDB"""

        popular_shows = []

        data = helpers.getURL(self.url, session=self.session, params=self.params, headers={'Referer': self.base_url}, returns='text')
        if not data:
            return None

        soup = BeautifulSoup(data, 'html5lib')
        results = soup.find_all("div", {"class": "lister-item"})

        for row in results:
            show = {}
            image_div = row.find("div", {"class": "lister-item-image"})
            if image_div:
                image = image_div.find("img")
                show['image_url_large'] = self.change_size(image['loadlate'], 3)
                show['imdb_tt'] = image['data-tconst']
                show['image_path'] = posixpath.join('images', 'imdb_popular', os.path.basename(show['image_url_large']))
                self.cache_image(show['image_url_large'])

            content = row.find("div", {"class": "lister-item-content"})
            if content:
                header = row.find("h3", {"class": "lister-item-header"})
                if header:
                    a_tag = header.find("a")
                    if a_tag:
                        show['name'] = a_tag.get_text(strip=True)
                        show['imdb_url'] = "http://www.imdb.com" + a_tag["href"]
                        show['year'] = header.find("span", {"class": "lister-item-year"}).contents[0].split(" ")[0][1:].strip("-")

                imdb_rating = row.find("div", {"class": "ratings-imdb-rating"})
                show['rating'] = imdb_rating['data-value'] if imdb_rating else None

                votes = row.find("span", {"name": "nv"})
                show['votes'] = votes['data-value'] if votes else None

                outline = content.find_all("p", {"class": "text-muted"})
                if outline and len(outline) >= 2:
                    show['outline'] = outline[1].contents[0].strip("\"")
                else:
                    show['outline'] = ''

                popular_shows.append(show)

        return popular_shows