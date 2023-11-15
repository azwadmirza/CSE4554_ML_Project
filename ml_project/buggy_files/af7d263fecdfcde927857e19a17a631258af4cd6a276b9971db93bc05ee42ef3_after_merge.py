def build(
    path_source,
    path_output,
    config,
    toc,
    warningiserror,
    nitpick,
    keep_going,
    freshenv,
    builder,
    custom_builder,
    verbose,
    quiet,
    individualpages,
    get_config_only=False,
):
    """Convert your book's or page's content to HTML or a PDF."""

    from .. import __version__ as jbv
    from ..sphinx import build_sphinx

    if not get_config_only:
        click.secho(f"Running Jupyter-Book v{jbv}", bold=True, fg="green")

    # Paths for the notebooks
    PATH_SRC_FOLDER = Path(path_source).absolute()

    config_overrides = {}
    found_config = find_config_path(PATH_SRC_FOLDER)
    BUILD_PATH = path_output if path_output is not None else found_config[0]

    # Set config for --individualpages option (pages, documents)
    if individualpages:
        if builder != "pdflatex":
            _error(
                """
                Specified option --individualpages only works with the
                following builders:

                pdflatex
                """
            )

    # Build Page
    if not PATH_SRC_FOLDER.is_dir():
        # it is a single file
        build_type = "page"
        subdir = None
        PATH_SRC = Path(path_source)
        PATH_SRC_FOLDER = PATH_SRC.parent.absolute()
        PAGE_NAME = PATH_SRC.with_suffix("").name

        # checking if the page is inside a sub directory
        # then changing the build_path accordingly
        if str(BUILD_PATH) in str(PATH_SRC_FOLDER):
            subdir = str(PATH_SRC_FOLDER.relative_to(BUILD_PATH))
        if subdir and subdir != ".":
            subdir = subdir.replace("/", "-")
            subdir = subdir + "-" + PAGE_NAME
            BUILD_PATH = Path(BUILD_PATH).joinpath("_build", "_page", subdir)
        else:
            BUILD_PATH = Path(BUILD_PATH).joinpath("_build", "_page", PAGE_NAME)

        # Find all files that *aren't* the page we're building and exclude them
        to_exclude = glob(str(PATH_SRC_FOLDER.joinpath("**", "*")), recursive=True)
        to_exclude = [
            op.relpath(ifile, PATH_SRC_FOLDER)
            for ifile in to_exclude
            if ifile != str(PATH_SRC.absolute())
        ]
        to_exclude.extend(["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"])

        # Now call the Sphinx commands to build
        config_overrides = {
            "master_doc": PAGE_NAME,
            "globaltoc_path": "",
            "exclude_patterns": to_exclude,
            "html_theme_options": {"single_page": True},
            # --individualpages option set to True for page call
            "latex_individualpages": True,
        }
    # Build Project
    else:
        build_type = "book"
        PAGE_NAME = None
        BUILD_PATH = Path(BUILD_PATH).joinpath("_build")

        # Table of contents
        if toc is None:
            toc = PATH_SRC_FOLDER.joinpath("_toc.yml")
        else:
            toc = Path(toc)

        if not toc.exists():
            _error(
                "Couldn't find a Table of Contents file. To auto-generate "
                f"one, run\n\n\tjupyter-book toc {path_source}"
            )

        # Check whether the table of contents has changed. If so we rebuild all
        build_files = list(BUILD_PATH.joinpath(".doctrees").rglob("*"))
        if toc and build_files:
            toc_modified = toc.stat().st_mtime

            build_modified = max([os.stat(ii).st_mtime for ii in build_files])

            # If the toc file has been modified after the build we need to force rebuild
            freshenv = toc_modified > build_modified

        config_overrides["globaltoc_path"] = toc.as_posix()

        # Builder-specific overrides
        if builder == "pdfhtml":
            config_overrides["html_theme_options"] = {"single_page": True}

        # --individualpages option passthrough
        config_overrides["latex_individualpages"] = individualpages

    # Use the specified configuration file, or one found in the root directory
    path_config = config or (
        found_config[0].joinpath("_config.yml") if found_config[1] else None
    )
    if path_config and not Path(path_config).exists():
        raise IOError(f"Config file path given, but not found: {path_config}")

    if builder in ["html", "pdfhtml", "linkcheck"]:
        OUTPUT_PATH = BUILD_PATH.joinpath("html")
    elif builder in ["latex", "pdflatex"]:
        OUTPUT_PATH = BUILD_PATH.joinpath("latex")
    elif builder in ["dirhtml"]:
        OUTPUT_PATH = BUILD_PATH.joinpath("dirhtml")
    elif builder in ["custom"]:
        OUTPUT_PATH = BUILD_PATH.joinpath(custom_builder)
        BUILDER_OPTS["custom"] = custom_builder

    if nitpick:
        config_overrides["nitpicky"] = True

    # If we only wan config (e.g. for printing/validation), stop here
    if get_config_only:
        return (path_config, PATH_SRC_FOLDER, config_overrides)

    # print information about the build
    click.echo(
        click.style("Source Folder: ", bold=True, fg="blue")
        + click.format_filename(f"{PATH_SRC_FOLDER}")
    )
    click.echo(
        click.style("Config Path: ", bold=True, fg="blue")
        + click.format_filename(f"{path_config}")
    )
    click.echo(
        click.style("Output Path: ", bold=True, fg="blue")
        + click.format_filename(f"{OUTPUT_PATH}")
    )

    # Now call the Sphinx commands to build
    result = build_sphinx(
        PATH_SRC_FOLDER,
        OUTPUT_PATH,
        toc,
        noconfig=True,
        path_config=path_config,
        confoverrides=config_overrides,
        builder=BUILDER_OPTS[builder],
        warningiserror=warningiserror,
        keep_going=keep_going,
        freshenv=freshenv,
        verbosity=verbose,
        quiet=quiet > 0,
        really_quiet=quiet > 1,
    )

    builder_specific_actions(
        result, builder, OUTPUT_PATH, build_type, PAGE_NAME, click.echo
    )