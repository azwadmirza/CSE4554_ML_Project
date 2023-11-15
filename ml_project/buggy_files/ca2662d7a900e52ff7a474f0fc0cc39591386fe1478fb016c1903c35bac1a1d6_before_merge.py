    def build(self, requirements, session, autobuilding=False):
        """Build wheels.

        :param unpack: If True, replace the sdist we built from with the
            newly built wheel, in preparation for installation.
        :return: True if all the wheels built correctly.
        """
        from pip._internal import index

        building_is_possible = self._wheel_dir or (
            autobuilding and self.wheel_cache.cache_dir
        )
        assert building_is_possible

        buildset = []
        for req in requirements:
            ephem_cache = False
            if req.constraint:
                continue
            if req.is_wheel:
                if not autobuilding:
                    logger.info(
                        'Skipping %s, due to already being wheel.', req.name,
                    )
            elif autobuilding and req.editable:
                pass
            elif autobuilding and req.link and not req.link.is_artifact:
                # VCS checkout. Build wheel just for this run.
                ephem_cache = True
            elif autobuilding and not req.source_dir:
                pass
            else:
                if autobuilding:
                    link = req.link
                    base, ext = link.splitext()
                    if index.egg_info_matches(base, None, link) is None:
                        # E.g. local directory. Build wheel just for this run.
                        ephem_cache = True
                    if "binary" not in index.fmt_ctl_formats(
                            self.finder.format_control,
                            canonicalize_name(req.name)):
                        logger.info(
                            "Skipping bdist_wheel for %s, due to binaries "
                            "being disabled for it.", req.name,
                        )
                        continue
                buildset.append((req, ephem_cache))

        if not buildset:
            return True

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
                        req.link = index.Link(path_to_url(wheel_file))
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
        # Return True if all builds were successful
        return len(build_failure) == 0