def parse_json_link_details(out_dir: str) -> Optional[Link]:
    """load the json link index from a given directory"""
    existing_index = os.path.join(out_dir, JSON_INDEX_FILENAME)
    if os.path.exists(existing_index):
        with open(existing_index, 'r', encoding='utf-8') as f:
            try:
                link_json = pyjson.load(f)
                return Link.from_json(link_json)
            except pyjson.JSONDecodeError:
                pass
    return None