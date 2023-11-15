    def open_data_docs(self, resource_identifier=None):
        """
        A stdlib cross-platform way to open a file in a browser.

        :param resource_identifier: ExpectationSuiteIdentifier, ValidationResultIdentifier
                or any other type's identifier. The argument is optional - when
                not supplied, the method returns the URL of the index page.
        """
        data_docs_urls = self.get_docs_sites_urls(resource_identifier=resource_identifier)
        for site_dict in data_docs_urls:
            logger.debug("Opening Data Docs found here: {}".format(site_dict["site_url"]))
            webbrowser.open(site_dict["site_url"])