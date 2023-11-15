    def open_data_docs(
        self, resource_identifier: Optional[str] = None, site_name: Optional[str] = None
    ) -> None:
        """
        A stdlib cross-platform way to open a file in a browser.

        Args:
            resource_identifier: ExpectationSuiteIdentifier,
                ValidationResultIdentifier or any other type's identifier. The
                argument is optional - when not supplied, the method returns the
                URL of the index page.
            site_name: Optionally specify which site to open. If not specified,
                open all docs found in the project.
        """
        data_docs_urls = self.get_docs_sites_urls(
            resource_identifier=resource_identifier, site_name=site_name,
        )
        urls_to_open = [site["site_url"] for site in data_docs_urls]

        for url in urls_to_open:
            logger.debug(f"Opening Data Docs found here: {url}")
            webbrowser.open(url)