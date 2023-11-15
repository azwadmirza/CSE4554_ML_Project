        def index(path):
            """
            Render the template for the onionshare landing page.
            """
            self.web.add_request(self.web.REQUEST_LOAD, request.path)

            # Deny new downloads if "Stop sharing after files have been sent" is checked and there is
            # currently a download
            deny_download = (
                self.web.settings.get("share", "autostop_sharing")
                and self.download_in_progress
            )
            if deny_download:
                r = make_response(render_template("denied.html"))
                return self.web.add_security_headers(r)

            # If download is allowed to continue, serve download page
            if self.should_use_gzip():
                self.filesize = self.gzip_filesize
            else:
                self.filesize = self.download_filesize

            return self.render_logic(path)