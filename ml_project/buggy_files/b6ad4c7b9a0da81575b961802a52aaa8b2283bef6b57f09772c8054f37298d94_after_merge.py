    def get_package_from_url(cls, url):  # type: (str) -> Package
        with temporary_directory() as temp_dir:
            temp_dir = Path(temp_dir)
            file_name = os.path.basename(urlparse.urlparse(url).path)
            download_file(url, str(temp_dir / file_name))

            package = cls.get_package_from_file(temp_dir / file_name)

        package._source_type = "url"
        package._source_url = url

        return package