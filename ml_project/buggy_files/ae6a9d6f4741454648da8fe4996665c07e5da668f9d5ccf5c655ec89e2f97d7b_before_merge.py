def is_valid(link: Link) -> bool:
    dir_exists = os.path.exists(link.link_dir)
    index_exists = os.path.exists(os.path.join(link.link_dir, 'index.json'))
    if not dir_exists:
        # unarchived links are not included in the valid list
        return False
    if dir_exists and not index_exists:
        return False
    if dir_exists and index_exists:
        try:
            parsed_link = parse_json_link_details(link.link_dir)
            return link.url == parsed_link.url
        except Exception:
            pass
    return False