    def get_docs_sites_urls(self, resource_identifier=None):
        """
        Get URLs for a resource for all data docs sites.

        This function will return URLs for any configured site even if the sites have not
        been built yet.

        :param resource_identifier: optional. It can be an identifier of ExpectationSuite's,
                ValidationResults and other resources that have typed identifiers.
                If not provided, the method will return the URLs of the index page.
        :return: a list of URLs. Each item is the URL for the resource for a data docs site
        """

        site_urls = []

        site_names = None
        sites = self._project_config_with_variables_substituted.data_docs_sites
        if sites:
            logger.debug("Found data_docs_sites.")

            for site_name, site_config in sites.items():
                if (site_names and site_name in site_names) or not site_names:
                    complete_site_config = site_config
                    module_name = 'great_expectations.render.renderer.site_builder'
                    site_builder = instantiate_class_from_config(
                        config=complete_site_config,
                        runtime_environment={
                            "data_context": self,
                            "root_directory": self.root_directory
                        },
                        config_defaults={
                            "module_name": module_name
                        }
                    )
                    if not site_builder:
                        raise ge_exceptions.ClassInstantiationError(
                            module_name=module_name,
                            package_name=None,
                            class_name=complete_site_config['class_name']
                        )
                    url = site_builder.get_resource_url(resource_identifier=resource_identifier)
                    site_urls.append({
                        "site_name": site_name,
                        "site_url": url
                    })

        return site_urls