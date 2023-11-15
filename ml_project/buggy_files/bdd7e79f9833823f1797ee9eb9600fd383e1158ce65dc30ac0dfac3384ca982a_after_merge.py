    def search(self, query):
        results = []

        search = {"q": query}

        response = session().get(self._base_url + "search", params=search)
        content = parse(response.content, namespaceHTMLElements=False)
        for result in content.findall(".//*[@class='package-snippet']"):
            name = result.find("h3/*[@class='package-snippet__name']").text
            version = result.find("h3/*[@class='package-snippet__version']").text

            if not name or not version:
                continue

            description = result.find("p[@class='package-snippet__description']").text
            if not description:
                description = ""

            try:
                result = Package(name, version, description)
                result.description = to_str(description.strip())
                results.append(result)
            except ParseVersionError:
                self._log(
                    'Unable to parse version "{}" for the {} package, skipping'.format(
                        version, name
                    ),
                    level="debug",
                )

        return results