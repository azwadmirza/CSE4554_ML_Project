    def prepare_files(self, finder, force_root_egg_info=False, bundle=False):
        """
        Prepare process. Create temp directories, download and/or unpack files.
        """
        unnamed = list(self.unnamed_requirements)
        reqs = list(self.requirements.values())
        while reqs or unnamed:
            if unnamed:
                req_to_install = unnamed.pop(0)
            else:
                req_to_install = reqs.pop(0)
            install = True
            best_installed = False
            not_found = None

            ###############################################
            ## Search for archive to fulfill requirement ##
            ###############################################

            if not self.ignore_installed and not req_to_install.editable:
                req_to_install.check_if_exists()
                if req_to_install.satisfied_by:
                    if self.upgrade:
                        if not self.force_reinstall and not req_to_install.url:
                            try:
                                url = finder.find_requirement(
                                    req_to_install, self.upgrade)
                            except BestVersionAlreadyInstalled:
                                best_installed = True
                                install = False
                            except DistributionNotFound as exc:
                                not_found = exc
                            else:
                                # Avoid the need to call find_requirement again
                                req_to_install.url = url.url

                        if not best_installed:
                            # don't uninstall conflict if user install and
                            # conflict is not user install
                            if not (self.use_user_site
                                    and not dist_in_usersite(
                                        req_to_install.satisfied_by
                                    )):
                                req_to_install.conflicts_with = \
                                    req_to_install.satisfied_by
                            req_to_install.satisfied_by = None
                    else:
                        install = False
                if req_to_install.satisfied_by:
                    if best_installed:
                        logger.notify('Requirement already up-to-date: %s'
                                      % req_to_install)
                    else:
                        logger.notify('Requirement already satisfied '
                                      '(use --upgrade to upgrade): %s'
                                      % req_to_install)
            if req_to_install.editable:
                logger.notify('Obtaining %s' % req_to_install)
            elif install:
                if (req_to_install.url
                        and req_to_install.url.lower().startswith('file:')):
                    logger.notify(
                        'Unpacking %s' %
                        display_path(url_to_path(req_to_install.url))
                    )
                else:
                    logger.notify('Downloading/unpacking %s' % req_to_install)
            logger.indent += 2

            ##################################
            ## vcs update or unpack archive ##
            ##################################

            try:
                is_bundle = False
                is_wheel = False
                if req_to_install.editable:
                    if req_to_install.source_dir is None:
                        location = req_to_install.build_location(self.src_dir)
                        req_to_install.source_dir = location
                    else:
                        location = req_to_install.source_dir
                    if not os.path.exists(self.build_dir):
                        _make_build_dir(self.build_dir)
                    req_to_install.update_editable(not self.is_download)
                    if self.is_download:
                        req_to_install.run_egg_info()
                        req_to_install.archive(self.download_dir)
                    else:
                        req_to_install.run_egg_info()
                elif install:
                    ##@@ if filesystem packages are not marked
                    ##editable in a req, a non deterministic error
                    ##occurs when the script attempts to unpack the
                    ##build directory

                    # NB: This call can result in the creation of a temporary
                    # build directory
                    location = req_to_install.build_location(
                        self.build_dir,
                        not self.is_download,
                    )
                    unpack = True
                    url = None

                    # In the case where the req comes from a bundle, we should
                    # assume a build dir exists and move on
                    if req_to_install.from_bundle:
                        pass
                    # If a checkout exists, it's unwise to keep going.  version
                    # inconsistencies are logged later, but do not fail the
                    # installation.
                    elif os.path.exists(os.path.join(location, 'setup.py')):
                        raise PreviousBuildDirError(
                            "pip can't proceed with requirements '%s' due to a"
                            " pre-existing buld directory (%s). This is likely"
                            " due to a previous installation that failed. pip "
                            "is being responsible and not assuming it can "
                            "delete this. Please delete it and try again." %
                            (req_to_install, location)
                        )
                    else:
                        ## FIXME: this won't upgrade when there's an existing
                        # package unpacked in `location`
                        if req_to_install.url is None:
                            if not_found:
                                raise not_found
                            url = finder.find_requirement(
                                req_to_install,
                                upgrade=self.upgrade,
                            )
                        else:
                            ## FIXME: should req_to_install.url already be a
                            # link?
                            url = Link(req_to_install.url)
                            assert url
                        if url:
                            try:

                                if (
                                    url.filename.endswith(wheel_ext)
                                    and self.wheel_download_dir
                                ):
                                    # when doing 'pip wheel`
                                    download_dir = self.wheel_download_dir
                                    do_download = True
                                else:
                                    download_dir = self.download_dir
                                    do_download = self.is_download
                                self.unpack_url(
                                    url, location, download_dir,
                                    do_download,
                                    )
                            except HTTPError as exc:
                                logger.fatal(
                                    'Could not install requirement %s because '
                                    'of error %s' % (req_to_install, exc)
                                )
                                raise InstallationError(
                                    'Could not install requirement %s because '
                                    'of HTTP error %s for URL %s' %
                                    (req_to_install, exc, url)
                                )
                        else:
                            unpack = False
                    if unpack:
                        is_bundle = req_to_install.is_bundle
                        is_wheel = url and url.filename.endswith(wheel_ext)
                        if is_bundle:
                            req_to_install.move_bundle_files(
                                self.build_dir,
                                self.src_dir,
                            )
                            for subreq in req_to_install.bundle_requirements():
                                reqs.append(subreq)
                                self.add_requirement(subreq)
                        elif self.is_download:
                            req_to_install.source_dir = location
                            if not is_wheel:
                                # FIXME:https://github.com/pypa/pip/issues/1112
                                req_to_install.run_egg_info()
                            if url and url.scheme in vcs.all_schemes:
                                req_to_install.archive(self.download_dir)

                        ##############################
                        ## parse wheel dependencies ##
                        ##############################

                        elif is_wheel:
                            req_to_install.source_dir = location
                            req_to_install.url = url.url
                            dist = list(
                                pkg_resources.find_distributions(location)
                            )[0]
                            if not req_to_install.req:
                                req_to_install.req = dist.as_requirement()
                                self.add_requirement(req_to_install)
                            if not self.ignore_dependencies:
                                for subreq in dist.requires(
                                        req_to_install.extras):
                                    if self.has_requirement(
                                            subreq.project_name):
                                        continue
                                    subreq = InstallRequirement(str(subreq),
                                                                req_to_install)
                                    reqs.append(subreq)
                                    self.add_requirement(subreq)
                        else:
                            req_to_install.source_dir = location
                            req_to_install.run_egg_info()
                            if force_root_egg_info:
                                # We need to run this to make sure that the
                                # .egg-info/ directory is created for packing
                                # in the bundle
                                req_to_install.run_egg_info(
                                    force_root_egg_info=True,
                                )
                            req_to_install.assert_source_matches_version()
                            #@@ sketchy way of identifying packages not grabbed
                            # from an index
                            if bundle and req_to_install.url:
                                self.copy_to_build_dir(req_to_install)
                                install = False
                        # req_to_install.req is only avail after unpack for URL
                        # pkgs repeat check_if_exists to uninstall-on-upgrade
                        # (#14)
                        if not self.ignore_installed:
                            req_to_install.check_if_exists()
                        if req_to_install.satisfied_by:
                            if self.upgrade or self.ignore_installed:
                                # don't uninstall conflict if user install and
                                # conflict is not user install
                                if not (self.use_user_site
                                        and not dist_in_usersite(
                                            req_to_install.satisfied_by)):
                                    req_to_install.conflicts_with = \
                                        req_to_install.satisfied_by
                                req_to_install.satisfied_by = None
                            else:
                                logger.notify(
                                    'Requirement already satisfied (use '
                                    '--upgrade to upgrade): %s' %
                                    req_to_install
                                )
                                install = False

                ##############################
                ## parse sdist dependencies ##
                ##############################

                if not (is_bundle or is_wheel):
                    ## FIXME: shouldn't be globally added:
                    finder.add_dependency_links(
                        req_to_install.dependency_links
                    )
                    if (req_to_install.extras):
                        logger.notify(
                            "Installing extra requirements: %r" %
                            ','.join(req_to_install.extras)
                        )
                    if not self.ignore_dependencies:
                        for req in req_to_install.requirements(
                                req_to_install.extras):
                            try:
                                name = pkg_resources.Requirement.parse(
                                    req
                                ).project_name
                            except ValueError as exc:
                                ## FIXME: proper warning
                                logger.error(
                                    'Invalid requirement: %r (%s) in '
                                    'requirement %s' %
                                    (req, exc, req_to_install)
                                )
                                continue
                            if self.has_requirement(name):
                                ## FIXME: check for conflict
                                continue
                            subreq = InstallRequirement(req, req_to_install)
                            reqs.append(subreq)
                            self.add_requirement(subreq)
                    if not self.has_requirement(req_to_install.name):
                        #'unnamed' requirements will get added here
                        self.add_requirement(req_to_install)
                    if (self.is_download
                            or req_to_install._temp_build_dir is not None):
                        self.reqs_to_cleanup.append(req_to_install)
                else:
                    self.reqs_to_cleanup.append(req_to_install)

                if install:
                    self.successfully_downloaded.append(req_to_install)
                    if (bundle
                            and (
                                req_to_install.url
                                and req_to_install.url.startswith('file:///')
                            )):
                        self.copy_to_build_dir(req_to_install)
            finally:
                logger.indent -= 2