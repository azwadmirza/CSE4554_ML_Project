    def check_other(self):
        """
        If the requirement is frozen somewhere other than pypi or github, skip.

        If you have a private pypi or use --extra-index-url, consider contributing
        support here.
        """
        if self.reqs:
            self.stdout.write(self.style.ERROR("\nOnly pypi and github based requirements are supported:"))
            for name, req in self.reqs.items():
                if "dist" in req:
                    pkg_info = "{dist.project_name} {dist.version}".format(dist=req["dist"])
                elif "url" in req:
                    pkg_info = "{url}".format(url=req["url"])
                else:
                    pkg_info = "unknown package"
                self.stdout.write(self.style.BOLD("{pkg_info:40} is not a pypi or github requirement".format(pkg_info=pkg_info)))