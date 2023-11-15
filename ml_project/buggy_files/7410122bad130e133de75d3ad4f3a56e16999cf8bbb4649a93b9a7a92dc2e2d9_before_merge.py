    def _link_package_versions(self, link, search):
        """Return an InstallationCandidate or None"""
        version = None
        if link.egg_fragment:
            egg_info = link.egg_fragment
            ext = link.ext
        else:
            egg_info, ext = link.splitext()
            if not ext:
                self._log_skipped_link(link, 'not a file')
                return
            if ext not in SUPPORTED_EXTENSIONS:
                self._log_skipped_link(
                    link, 'unsupported archive format: %s' % ext,
                )
                return
            if "binary" not in search.formats and ext == wheel_ext:
                self._log_skipped_link(
                    link, 'No binaries permitted for %s' % search.supplied,
                )
                return
            if "macosx10" in link.path and ext == '.zip':
                self._log_skipped_link(link, 'macosx10 one')
                return
            if ext == wheel_ext:
                try:
                    wheel = Wheel(link.filename)
                except InvalidWheelFilename:
                    self._log_skipped_link(link, 'invalid wheel filename')
                    return
                if canonicalize_name(wheel.name) != search.canonical:
                    self._log_skipped_link(
                        link, 'wrong project name (not %s)' % search.supplied)
                    return

                if not wheel.supported(self.valid_tags):
                    self._log_skipped_link(
                        link, 'it is not compatible with this Python')
                    return

                version = wheel.version

        # This should be up by the search.ok_binary check, but see issue 2700.
        if "source" not in search.formats and ext != wheel_ext:
            self._log_skipped_link(
                link, 'No sources permitted for %s' % search.supplied,
            )
            return

        if not version:
            version = egg_info_matches(egg_info, search.supplied, link)
        if version is None:
            self._log_skipped_link(
                link, 'Missing project version for %s' % search.supplied)
            return

        match = self._py_version_re.search(version)
        if match:
            version = version[:match.start()]
            py_version = match.group(1)
            if py_version != sys.version[:3]:
                self._log_skipped_link(
                    link, 'Python version is incorrect')
                return
        try:
            support_this_python = check_requires_python(link.requires_python)
        except specifiers.InvalidSpecifier:
            logger.debug("Package %s has an invalid Requires-Python entry: %s",
                         link.filename, link.requires_python)
            support_this_python = True

        if not support_this_python:
            logger.debug("The package %s is incompatible with the python"
                         "version in use. Acceptable python versions are:%s",
                         link, link.requires_python)
            return
        logger.debug('Found link %s, version: %s', link, version)

        return InstallationCandidate(search.supplied, version, link)