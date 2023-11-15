def get_unrecognized_folders(links, out_dir: str=OUTPUT_DIR) -> Dict[str, Optional[Link]]:
    """dirs that don't contain recognizable archive data and aren't listed in the main index"""
    by_timestamp = {link.timestamp: 0 for link in links}
    unrecognized_folders: Dict[str, Optional[Link]] = {}

    for entry in os.scandir(os.path.join(out_dir, ARCHIVE_DIR_NAME)):
        if entry.is_dir(follow_symlinks=True):
            index_exists = os.path.exists(os.path.join(entry.path, 'index.json'))
            link = None
            try:
                link = parse_json_link_details(entry.path)
            except Exception:
                pass

            if index_exists and link is None:
                # index exists but it's corrupted or unparseable
                unrecognized_folders[entry.path] = link
            
            elif not index_exists:
                # link details index doesn't exist and the folder isn't in the main index
                timestamp = entry.path.rsplit('/', 1)[-1]
                if timestamp not in by_timestamp:
                    unrecognized_folders[entry.path] = link

    return unrecognized_folders