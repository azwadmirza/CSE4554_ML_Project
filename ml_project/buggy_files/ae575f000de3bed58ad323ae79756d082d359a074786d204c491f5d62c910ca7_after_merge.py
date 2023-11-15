    def unpack_url(self, link, location, download_dir=None,
                   only_download=False):
        if download_dir is None:
            download_dir = self.download_dir

        # non-editable vcs urls
        if is_vcs_url(link):
            unpack_vcs_link(link, location, only_download)

        # file urls
        elif is_file_url(link):
            unpack_file_url(link, location, download_dir)
            if only_download:
                write_delete_marker_file(location)

        # http urls
        else:
            unpack_http_url(
                link,
                location,
                download_dir,
                self.session,
            )
            if only_download:
                write_delete_marker_file(location)