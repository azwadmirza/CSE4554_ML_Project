    def build(
        self,
        requirements,  # type: Iterable[InstallRequirement]
        session,  # type: PipSession
        autobuilding=False  # type: bool
    ):
        # type: (...) -> List[InstallRequirement]
        """Build wheels.

        :param unpack: If True, replace the sdist we built from with the
            newly built wheel, in preparation for installation.
        :return: True if all the wheels built correctly.
        """
        buildset = []
        format_control = self.finder.format_control
        # Whether a cache directory is available for autobuilding=True.
        cache_available = bool(self._wheel_dir or self.wheel_cache.cache_dir)

        for req in requirements:
            ephem_cache = should_use_ephemeral_cache(
                req, format_control=format_control, autobuilding=autobuilding,
                cache_available=cache_available,
            )
            if ephem_cache is None:
                continue

            buildset.append((req, ephem_cache))

        if not buildset:
            return []

        # Is any wheel build not using the ephemeral cache?
        if any(not ephem_cache for _, ephem_cache in buildset):
            have_directory_for_build = self._wheel_dir or (
                autobuilding and self.wheel_cache.cache_dir
            )
            assert have_directory_for_build

        # TODO by @pradyunsg
        # Should break up this method into 2 separate methods.

        # Build the wheels.
        logger.info(
            'Building wheels for collected packages: %s',
            ', '.join([req.name for (req, _) in buildset]),
        )
        _cache = self.wheel_cache  # shorter name
        with indent_log():
            build_success, build_failure = [], []
            for req, ephem in buildset:
                python_tag = None
                if autobuilding:
                    python_tag = pep425tags.implementation_tag
                    if ephem:
                        output_dir = _cache.get_ephem_path_for_link(req.link)
                    else:
                        output_dir = _cache.get_path_for_link(req.link)
                    try:
                        ensure_dir(output_dir)
                    except OSError as e:
                        logger.warning("Building wheel for %s failed: %s",
                                       req.name, e)
                        build_failure.append(req)
                        continue
                else:
                    output_dir = self._wheel_dir
                wheel_file = self._build_one(
                    req, output_dir,
                    python_tag=python_tag,
                )
                if wheel_file:
                    build_success.append(req)
                    if autobuilding:
                        # XXX: This is mildly duplicative with prepare_files,
                        # but not close enough to pull out to a single common
                        # method.
                        # The code below assumes temporary source dirs -
                        # prevent it doing bad things.
                        if req.source_dir and not os.path.exists(os.path.join(
                                req.source_dir, PIP_DELETE_MARKER_FILENAME)):
                            raise AssertionError(
                                "bad source dir - missing marker")
                        # Delete the source we built the wheel from
                        req.remove_temporary_source()
                        # set the build directory again - name is known from
                        # the work prepare_files did.
                        req.source_dir = req.build_location(
                            self.preparer.build_dir
                        )
                        # Update the link for this.
                        req.link = Link(path_to_url(wheel_file))
                        assert req.link.is_wheel
                        # extract the wheel into the dir
                        unpack_url(
                            req.link, req.source_dir, None, False,
                            session=session,
                        )
                else:
                    build_failure.append(req)

        # notify success/failure
        if build_success:
            logger.info(
                'Successfully built %s',
                ' '.join([req.name for req in build_success]),
            )
        if build_failure:
            logger.info(
                'Failed to build %s',
                ' '.join([req.name for req in build_failure]),
            )
        # Return a list of requirements that failed to build
        return build_failure