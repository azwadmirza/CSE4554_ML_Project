    def choose_for(self, package):  # type: (Package) -> Link
        """
        Return the url of the selected archive for a given package.
        """
        links = []
        for link in self._get_links(package):
            if link.is_wheel and not Wheel(link.filename).is_supported_by_environment(
                self._env
            ):
                continue

            if link.ext in {".egg", ".exe", ".msi", ".rpm", ".srpm"}:
                continue

            links.append(link)

        if not links:
            raise RuntimeError(
                "Unable to find installation candidates for {}".format(package)
            )

        # Get the best link
        chosen = max(links, key=lambda link: self._sort_key(package, link))
        if not chosen:
            raise RuntimeError(
                "Unable to find installation candidates for {}".format(package)
            )

        return chosen