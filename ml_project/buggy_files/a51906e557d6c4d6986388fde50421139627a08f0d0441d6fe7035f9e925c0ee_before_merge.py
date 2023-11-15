    def check_pypi(self):
        """
        If the requirement is frozen to pypi, check for a new version.
        """
        for dist in get_installed_distributions():
            name = dist.project_name
            if name in self.reqs.keys():
                self.reqs[name]["dist"] = dist

        pypi = ServerProxy("https://pypi.python.org/pypi")
        for name, req in list(self.reqs.items()):
            if req["url"]:
                continue  # skipping github packages.
            elif "dist" in req:
                dist = req["dist"]
                dist_version = LooseVersion(dist.version)
                available = pypi.package_releases(req["pip_req"].name, True) or pypi.package_releases(req["pip_req"].name.replace('-', '_'), True)
                available_version = self._available_version(dist_version, available)

                if not available_version:
                    msg = self.style.WARN("release is not on pypi (check capitalization and/or --extra-index-url)")
                elif self.options['show_newer'] and dist_version > available_version:
                    msg = self.style.INFO("{0} available (newer installed)".format(available_version))
                elif available_version > dist_version:
                    msg = self.style.INFO("{0} available".format(available_version))
                else:
                    msg = "up to date"
                    del self.reqs[name]
                    continue
                pkg_info = self.style.BOLD("{dist.project_name} {dist.version}".format(dist=dist))
            else:
                msg = "not installed"
                pkg_info = name
            print("{pkg_info:40} {msg}".format(pkg_info=pkg_info, msg=msg))
            del self.reqs[name]