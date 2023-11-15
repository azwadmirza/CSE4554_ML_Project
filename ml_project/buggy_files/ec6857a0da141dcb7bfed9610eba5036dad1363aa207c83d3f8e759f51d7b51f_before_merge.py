def _install_wheel(
    name,  # type: str
    wheel_zip,  # type: ZipFile
    wheel_path,  # type: str
    scheme,  # type: Scheme
    pycompile=True,  # type: bool
    warn_script_location=True,  # type: bool
    direct_url=None,  # type: Optional[DirectUrl]
    requested=False,  # type: bool
):
    # type: (...) -> None
    """Install a wheel.

    :param name: Name of the project to install
    :param wheel_zip: open ZipFile for wheel being installed
    :param scheme: Distutils scheme dictating the install directories
    :param req_description: String used in place of the requirement, for
        logging
    :param pycompile: Whether to byte-compile installed Python files
    :param warn_script_location: Whether to check that scripts are installed
        into a directory on PATH
    :raises UnsupportedWheel:
        * when the directory holds an unpacked wheel with incompatible
          Wheel-Version
        * when the .dist-info dir does not match the wheel
    """
    info_dir, metadata = parse_wheel(wheel_zip, name)

    if wheel_root_is_purelib(metadata):
        lib_dir = scheme.purelib
    else:
        lib_dir = scheme.platlib

    # Record details of the files moved
    #   installed = files copied from the wheel to the destination
    #   changed = files changed while installing (scripts #! line typically)
    #   generated = files newly generated during the install (script wrappers)
    installed = {}  # type: Dict[RecordPath, RecordPath]
    changed = set()  # type: Set[RecordPath]
    generated = []  # type: List[str]

    def record_installed(srcfile, destfile, modified=False):
        # type: (RecordPath, text_type, bool) -> None
        """Map archive RECORD paths to installation RECORD paths."""
        newpath = _fs_to_record_path(destfile, lib_dir)
        installed[srcfile] = newpath
        if modified:
            changed.add(_fs_to_record_path(destfile))

    def all_paths():
        # type: () -> Iterable[RecordPath]
        names = wheel_zip.namelist()
        # If a flag is set, names may be unicode in Python 2. We convert to
        # text explicitly so these are valid for lookup in RECORD.
        decoded_names = map(ensure_text, names)
        for name in decoded_names:
            yield cast("RecordPath", name)

    def is_dir_path(path):
        # type: (RecordPath) -> bool
        return path.endswith("/")

    def assert_no_path_traversal(dest_dir_path, target_path):
        # type: (text_type, text_type) -> None
        if not is_within_directory(dest_dir_path, target_path):
            message = (
                "The wheel {!r} has a file {!r} trying to install"
                " outside the target directory {!r}"
            )
            raise InstallationError(
                message.format(wheel_path, target_path, dest_dir_path)
            )

    def root_scheme_file_maker(zip_file, dest):
        # type: (ZipFile, text_type) -> Callable[[RecordPath], File]
        def make_root_scheme_file(record_path):
            # type: (RecordPath) -> File
            normed_path = os.path.normpath(record_path)
            dest_path = os.path.join(dest, normed_path)
            assert_no_path_traversal(dest, dest_path)
            return ZipBackedFile(record_path, dest_path, zip_file)

        return make_root_scheme_file

    def data_scheme_file_maker(zip_file, scheme):
        # type: (ZipFile, Scheme) -> Callable[[RecordPath], File]
        scheme_paths = {}
        for key in SCHEME_KEYS:
            encoded_key = ensure_text(key)
            scheme_paths[encoded_key] = ensure_text(
                getattr(scheme, key), encoding=sys.getfilesystemencoding()
            )

        def make_data_scheme_file(record_path):
            # type: (RecordPath) -> File
            normed_path = os.path.normpath(record_path)
            _, scheme_key, dest_subpath = normed_path.split(os.path.sep, 2)
            scheme_path = scheme_paths[scheme_key]
            dest_path = os.path.join(scheme_path, dest_subpath)
            assert_no_path_traversal(scheme_path, dest_path)
            return ZipBackedFile(record_path, dest_path, zip_file)

        return make_data_scheme_file

    def is_data_scheme_path(path):
        # type: (RecordPath) -> bool
        return path.split("/", 1)[0].endswith(".data")

    paths = all_paths()
    file_paths = filterfalse(is_dir_path, paths)
    root_scheme_paths, data_scheme_paths = partition(
        is_data_scheme_path, file_paths
    )

    make_root_scheme_file = root_scheme_file_maker(
        wheel_zip,
        ensure_text(lib_dir, encoding=sys.getfilesystemencoding()),
    )
    files = map(make_root_scheme_file, root_scheme_paths)

    def is_script_scheme_path(path):
        # type: (RecordPath) -> bool
        parts = path.split("/", 2)
        return (
            len(parts) > 2 and
            parts[0].endswith(".data") and
            parts[1] == "scripts"
        )

    other_scheme_paths, script_scheme_paths = partition(
        is_script_scheme_path, data_scheme_paths
    )

    make_data_scheme_file = data_scheme_file_maker(wheel_zip, scheme)
    other_scheme_files = map(make_data_scheme_file, other_scheme_paths)
    files = chain(files, other_scheme_files)

    # Get the defined entry points
    distribution = pkg_resources_distribution_for_wheel(
        wheel_zip, name, wheel_path
    )
    console, gui = get_entrypoints(distribution)

    def is_entrypoint_wrapper(file):
        # type: (File) -> bool
        # EP, EP.exe and EP-script.py are scripts generated for
        # entry point EP by setuptools
        path = file.dest_path
        name = os.path.basename(path)
        if name.lower().endswith('.exe'):
            matchname = name[:-4]
        elif name.lower().endswith('-script.py'):
            matchname = name[:-10]
        elif name.lower().endswith(".pya"):
            matchname = name[:-4]
        else:
            matchname = name
        # Ignore setuptools-generated scripts
        return (matchname in console or matchname in gui)

    script_scheme_files = map(make_data_scheme_file, script_scheme_paths)
    script_scheme_files = filterfalse(
        is_entrypoint_wrapper, script_scheme_files
    )
    script_scheme_files = map(ScriptFile, script_scheme_files)
    files = chain(files, script_scheme_files)

    for file in files:
        file.save()
        record_installed(file.src_record_path, file.dest_path, file.changed)

    def pyc_source_file_paths():
        # type: () -> Iterator[text_type]
        # We de-duplicate installation paths, since there can be overlap (e.g.
        # file in .data maps to same location as file in wheel root).
        # Sorting installation paths makes it easier to reproduce and debug
        # issues related to permissions on existing files.
        for installed_path in sorted(set(installed.values())):
            full_installed_path = os.path.join(lib_dir, installed_path)
            if not os.path.isfile(full_installed_path):
                continue
            if not full_installed_path.endswith('.py'):
                continue
            yield full_installed_path

    def pyc_output_path(path):
        # type: (text_type) -> text_type
        """Return the path the pyc file would have been written to.
        """
        if PY2:
            if sys.flags.optimize:
                return path + 'o'
            else:
                return path + 'c'
        else:
            return importlib.util.cache_from_source(path)

    # Compile all of the pyc files for the installed files
    if pycompile:
        with captured_stdout() as stdout:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                for path in pyc_source_file_paths():
                    # Python 2's `compileall.compile_file` requires a str in
                    # error cases, so we must convert to the native type.
                    path_arg = ensure_str(
                        path, encoding=sys.getfilesystemencoding()
                    )
                    success = compileall.compile_file(
                        path_arg, force=True, quiet=True
                    )
                    if success:
                        pyc_path = pyc_output_path(path)
                        assert os.path.exists(pyc_path)
                        pyc_record_path = cast(
                            "RecordPath", pyc_path.replace(os.path.sep, "/")
                        )
                        record_installed(pyc_record_path, pyc_path)
        logger.debug(stdout.getvalue())

    maker = PipScriptMaker(None, scheme.scripts)

    # Ensure old scripts are overwritten.
    # See https://github.com/pypa/pip/issues/1800
    maker.clobber = True

    # Ensure we don't generate any variants for scripts because this is almost
    # never what somebody wants.
    # See https://bitbucket.org/pypa/distlib/issue/35/
    maker.variants = {''}

    # This is required because otherwise distlib creates scripts that are not
    # executable.
    # See https://bitbucket.org/pypa/distlib/issue/32/
    maker.set_mode = True

    # Generate the console and GUI entry points specified in the wheel
    scripts_to_generate = get_console_script_specs(console)

    gui_scripts_to_generate = list(starmap('{} = {}'.format, gui.items()))

    generated_console_scripts = maker.make_multiple(scripts_to_generate)
    generated.extend(generated_console_scripts)

    generated.extend(
        maker.make_multiple(gui_scripts_to_generate, {'gui': True})
    )

    if warn_script_location:
        msg = message_about_scripts_not_on_PATH(generated_console_scripts)
        if msg is not None:
            logger.warning(msg)

    generated_file_mode = 0o666 & ~current_umask()

    @contextlib.contextmanager
    def _generate_file(path, **kwargs):
        # type: (str, **Any) -> Iterator[NamedTemporaryFileResult]
        with adjacent_tmp_file(path, **kwargs) as f:
            yield f
        os.chmod(f.name, generated_file_mode)
        replace(f.name, path)

    dest_info_dir = os.path.join(lib_dir, info_dir)

    # Record pip as the installer
    installer_path = os.path.join(dest_info_dir, 'INSTALLER')
    with _generate_file(installer_path) as installer_file:
        installer_file.write(b'pip\n')
    generated.append(installer_path)

    # Record the PEP 610 direct URL reference
    if direct_url is not None:
        direct_url_path = os.path.join(dest_info_dir, DIRECT_URL_METADATA_NAME)
        with _generate_file(direct_url_path) as direct_url_file:
            direct_url_file.write(direct_url.to_json().encode("utf-8"))
        generated.append(direct_url_path)

    # Record the REQUESTED file
    if requested:
        requested_path = os.path.join(dest_info_dir, 'REQUESTED')
        with open(requested_path, "w"):
            pass
        generated.append(requested_path)

    record_text = distribution.get_metadata('RECORD')
    record_rows = list(csv.reader(record_text.splitlines()))

    rows = get_csv_rows_for_installed(
        record_rows,
        installed=installed,
        changed=changed,
        generated=generated,
        lib_dir=lib_dir)

    # Record details of all files installed
    record_path = os.path.join(dest_info_dir, 'RECORD')

    with _generate_file(record_path, **csv_io_kwargs('w')) as record_file:
        # The type mypy infers for record_file is different for Python 3
        # (typing.IO[Any]) and Python 2 (typing.BinaryIO). We explicitly
        # cast to typing.IO[str] as a workaround.
        writer = csv.writer(cast('IO[str]', record_file))
        writer.writerows(_normalized_outrows(rows))