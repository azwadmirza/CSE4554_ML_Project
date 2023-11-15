    def get_package(self, package_reference, dest_folder):
        """Gets a dict of filename:contents from package"""
        url = "%s/conans/%s/packages/%s/download_urls" % (self._remote_api_url,
                                                          "/".join(package_reference.conan),
                                                          package_reference.package_id)
        urls = self._get_json(url)
        if not urls:
            raise NotFoundException("Package not found!")
        # TODO: Get fist an snapshot and compare files and download only required?

        # Download the resources
        file_paths = self.download_files_to_folder(urls, dest_folder, self._output)
        return file_paths