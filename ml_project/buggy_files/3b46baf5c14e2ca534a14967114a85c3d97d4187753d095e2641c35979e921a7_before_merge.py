    def get_package(self, package_reference):
        """Gets a dict of filename:contents from package"""
        url = "%s/conans/%s/packages/%s/download_urls" % (self._remote_api_url,
                                                          "/".join(package_reference.conan),
                                                          package_reference.package_id)
        urls = self._get_json(url)
        if not urls:
            raise NotFoundException("Package not found!")
        # TODO: Get fist an snapshot and compare files and download only required?

        # Download the resources
        contents = self.download_files(urls, self._output)
        return contents