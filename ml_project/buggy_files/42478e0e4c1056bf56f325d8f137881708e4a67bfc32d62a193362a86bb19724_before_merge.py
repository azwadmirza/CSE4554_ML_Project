def parse_json_links_details(out_dir: str) -> Iterator[Link]:
    """read through all the archive data folders and return the parsed links"""

    for entry in os.scandir(os.path.join(out_dir, ARCHIVE_DIR_NAME)):
        if entry.is_dir(follow_symlinks=True):
            if os.path.exists(os.path.join(entry.path, 'index.json')):
                link = parse_json_link_details(entry.path)
                if link:
                    yield link