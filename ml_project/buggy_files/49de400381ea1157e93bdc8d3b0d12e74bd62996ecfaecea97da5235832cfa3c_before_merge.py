def _build_one_inside_env(
    req,  # type: InstallRequirement
    output_dir,  # type: str
    build_options,  # type: List[str]
    global_options,  # type: List[str]
):
    # type: (...) -> Optional[str]
    with TempDirectory(kind="wheel") as temp_dir:
        if req.use_pep517:
            wheel_path = build_wheel_pep517(
                name=req.name,
                backend=req.pep517_backend,
                metadata_directory=req.metadata_directory,
                build_options=build_options,
                tempd=temp_dir.path,
            )
        else:
            wheel_path = build_wheel_legacy(
                name=req.name,
                setup_py_path=req.setup_py_path,
                source_dir=req.unpacked_source_directory,
                global_options=global_options,
                build_options=build_options,
                tempd=temp_dir.path,
            )

        if wheel_path is not None:
            wheel_name = os.path.basename(wheel_path)
            dest_path = os.path.join(output_dir, wheel_name)
            try:
                wheel_hash, length = hash_file(wheel_path)
                shutil.move(wheel_path, dest_path)
                logger.info('Created wheel for %s: '
                            'filename=%s size=%d sha256=%s',
                            req.name, wheel_name, length,
                            wheel_hash.hexdigest())
                logger.info('Stored in directory: %s', output_dir)
                return dest_path
            except Exception as e:
                logger.warning(
                    "Building wheel for %s failed: %s",
                    req.name, e,
                )
        # Ignore return, we can't do anything else useful.
        _clean_one(req, global_options)
        return None