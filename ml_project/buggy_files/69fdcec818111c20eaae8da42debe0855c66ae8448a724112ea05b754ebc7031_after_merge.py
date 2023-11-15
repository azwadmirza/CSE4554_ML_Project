def find_fragments(base_directory, sections, fragment_directory, definitions):
    """
    Sections are a dictonary of section names to paths.
    """
    content = OrderedDict()
    fragment_filenames = []

    for key, val in sections.items():

        if fragment_directory is not None:
            section_dir = os.path.join(base_directory, val, fragment_directory)
        else:
            section_dir = os.path.join(base_directory, val)

        if sys.version_info >= (3,):
            expected_exception = FileNotFoundError
        else:
            expected_exception = OSError

        try:
            files = os.listdir(section_dir)
        except expected_exception as e:
            message = "Failed to list the news fragment files.\n{}".format(
                ''.join(traceback.format_exception_only(type(e), e)),
            )
            raise ConfigError(message)

        file_content = {}

        for basename in files:

            ticket, category, counter = parse_newfragment_basename(
                basename, definitions
            )
            if category is None:
                continue

            full_filename = os.path.join(section_dir, basename)
            fragment_filenames.append(full_filename)
            with open(full_filename, "rb") as f:
                data = f.read().decode("utf8", "replace")

            if (ticket, category, counter) in file_content:
                raise ValueError(
                    "multiple files for {}.{} in {}".format(
                        ticket, category, section_dir
                    )
                )
            file_content[ticket, category, counter] = data

        content[key] = file_content

    return content, fragment_filenames