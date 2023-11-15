    def get_docs_sites_urls(
        self, resource_identifier=None, site_name: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get URLs for a resource for all data docs sites.

        This function will return URLs for any configured site even if the sites
        have not been built yet.

        Args:
            resource_identifier (object): optional. It can be an identifier of
                ExpectationSuite's, ValidationResults and other resources that
                have typed identifiers. If not provided, the method will return
                the URLs of the index page.
            site_name: Optionally specify which site to open. If not specified,
                return all urls in the project.

        Returns:
            list: a list of URLs. Each item is the URL for the resource for a
                data docs site
        """
        sites = self._project_config_with_variables_substituted.data_docs_sites
        if not sites:
            logger.debug("Found no data_docs_sites.")
            return []
        logger.debug(f"Found {len(sites)} data_docs_sites.")

        if site_name:
            if site_name not in sites.keys():
                raise ge_exceptions.DataContextError(f"Could not find site named {site_name}. Please check your configurations")
            site = sites[site_name]
            site_builder = self._load_site_builder_from_site_config(site)
            url = site_builder.get_resource_url(resource_identifier=resource_identifier)
            return [{"site_name": site_name, "site_url": url}]

        site_urls = []
        for _site_name, site_config in sites.items():
            site_builder = self._load_site_builder_from_site_config(site_config)
            url = site_builder.get_resource_url(resource_identifier=resource_identifier)
            site_urls.append({"site_name": _site_name, "site_url": url})

        return site_urls